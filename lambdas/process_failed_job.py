import json

COMPUTE_RESOURCES_VCPUS_MEMORY = (
    (0.25, 512),
    (0.25, 1024),
    (0.25, 2048),
    (0.5, 3072),
    (0.5, 4096),
    (1, 4096),
    (1, 5120),
    (1, 6144),
    (1, 7168),
    (1, 8192),
    (2, 9216),
    (2, 10240),
    (2, 11264),
    (2, 12288),
    (2, 13312),
    (2, 14336),
    (2, 15360),
    (2, 16384),
    (4, 17408),
    (4, 18432),
    (4, 19456),
    (4, 20480),
    (4, 21504),
    (4, 22528),
    (4, 23552),
    (4, 24576),
    (4, 25600),
    (4, 26624),
    (4, 27648),
    (4, 28672),
    (4, 29696),
    (4, 30720),
    (8, 32768),
    (8, 36864),
    (8, 40960),
    (8, 45056),
    (8, 49152),
    (8, 53248),
    (8, 57344),
    (8, 61440),
)


def _get_next_resource_specs(current_vcpus, current_memory):
    current_vcpus = float(current_vcpus)
    current_memory = int(current_memory)
    current_index = None
    for i, compute_spec in enumerate(COMPUTE_RESOURCES_VCPUS_MEMORY):
        if current_vcpus == compute_spec[0] and current_memory == compute_spec[1]:
            current_index = i
    if current_index == len(COMPUTE_RESOURCES_VCPUS_MEMORY) - 1:
        raise Exception("Reached memory resources limit (VCPUs and Memory)")
    return COMPUTE_RESOURCES_VCPUS_MEMORY[current_index + 1]


def handler(event, context):
    job_error = event["job_error"]["Cause"]
    try:
        batch_metadata = json.loads(job_error)
    except json.decoder.JSONDecodeError:
        return {"retry_job": False, "retry_job_specifications": None}

    job_name = event["job_name"]
    job_command = event["job_command"]
    exit_code = batch_metadata["Attempts"][0]["Container"]["ExitCode"]
    if exit_code == 137:
        current_vcpus = event["job_vcpus"]
        current_memory = event["job_memory"]
        next_vcpus, next_memory = _get_next_resource_specs(current_vcpus, current_memory)
        return {
            "retry_job": True,
            "retry_job_specifications": {
                "job_command": job_command,
                "job_name": job_name,
                "job_vcpus": str(next_vcpus),
                "job_memory": str(next_memory),
            },
        }
    else:
        return {"retry_job": False, "retry_job_specifications": None}
