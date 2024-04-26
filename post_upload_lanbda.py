import requests
import time

# URLs for the APIs
headers = {"Authorization": "<Replace with token>"}


def call_sync_api(SYNC_API_URL):
    """ Call the sync API to initiate a sync and return the sync_id """
    response = requests.post(SYNC_API_URL, headers= headers, json={})
    response.raise_for_status()  # Raise an exception for HTTP error responses
    return response.json()['id']

def check_status(STATUS_API_URL,trigger_id):
    """ Continuously poll the status API until the sync is completed """
    while True:
        response = requests.get(f"{STATUS_API_URL}/{trigger_id}", headers= headers)
        response.raise_for_status()
        status = response.json()['status']
        if status == "SUCCESS":
            print("Sync SUCCESS!")
            break
        elif status == "FAILED":
            raise Exception("Sync job failed")
        else:
            print(f"Current status: {status}. Checking again in 10 seconds.")
            time.sleep(10)

def get_import_jobs(GET_IMPORT_JOBS_URL):
    """ Call the get import jobs API and return a list of job IDs """
    response = requests.get(GET_IMPORT_JOBS_URL, headers= headers)
    response.raise_for_status()
    return response.json()['import_jobs']

def run_pipeline_validate(RUN_VALIDATE_URL,payload):
    response = requests.post(f"{RUN_VALIDATE_URL}", headers= headers, json=payload)
    response.raise_for_status()
    print(f"Start for job {payload} initiated.")


def start(START, payload):
    """ Call the run validate API for a given job_id """
    response = requests.put(f"{START}", headers= headers, json=payload)
    response.raise_for_status()
    print(f"Validation for job {payload} initiated.")
    

def main():
    SYNC_API_URL = "https://datapipes.api.test.aws.datapipes.cldcvr.dev/ingestor/v2/import"
    STATUS_API_URL = "https://datapipes.api.test.aws.datapipes.cldcvr.dev/ingestor/v2/import/trigger" 
    
    def import_pipelines():
        GET_IMPORT_PIPELINE_JOBS_URL = "https://datapipes.api.test.aws.datapipes.cldcvr.dev/ingestor/v2/import/jobs?entity_type=PIPELINE&page_size=300&offset_token="
        RUN_VALIDATE_PIPELINE_URL = "https://datapipes.api.test.aws.datapipes.cldcvr.dev/ingestor/v2/import/validate/pipelines"
        START_PIPELINES="https://datapipes.api.test.aws.datapipes.cldcvr.dev/ingestor/v2/import/pipeline/start"
        # Step 1: Call sync API
        trigger_id = call_sync_api(SYNC_API_URL)
        print(f"trigger_id: {trigger_id}")

        # Step 2: Check status until completed
        check_status(STATUS_API_URL,trigger_id)

        # Step 3: Get import jobs
        pipeline_jobs = get_import_jobs(GET_IMPORT_PIPELINE_JOBS_URL)
        print(pipeline_jobs)
        # print(f"Retrieved {len(pipeline_jobs)} jobs to validate.")

        # Step 4: Run validate on each job
        
        pipeline_import_ids = []
        for job in pipeline_jobs:
            print(f"pipeline_import_ids job: {job}")
            if not job["is_validated"] and not job["entity_created"]:
                pipeline_import_ids.append(job["id"])
        
        payload=  {
            "force_update": True,
            "import_ids": pipeline_import_ids
        }
        print(f"pipeline_import_ids: {pipeline_import_ids}")
        if pipeline_import_ids:
            run_pipeline_validate(RUN_VALIDATE_PIPELINE_URL,payload)
        
            running_pipelines = set()
            while True:
                pipeline_jobs = get_import_jobs(GET_IMPORT_PIPELINE_JOBS_URL)
                for job in pipeline_jobs:
                    print(f"job: {job}, {job['status']}")
                    if job["status"] in ["SUCCESS", "FAILED"] and job["id"] in pipeline_import_ids:
                        running_pipelines.add(job["id"])
                print(len(running_pipelines),len(pipeline_import_ids))
                if len(running_pipelines) == len(pipeline_import_ids):
                    break
                
                time.sleep(10)
        
        print("Validation completed.")
        validate_pipeline_jobs = []
        pipeline_jobs = get_import_jobs(GET_IMPORT_PIPELINE_JOBS_URL)
        for job in pipeline_jobs:
            if job["is_validated"] and not job["entity_created"]:
                validate_pipeline_jobs.append(job["id"])
        
        payload ={
            "start_pipeline": True,
            "import_ids": validate_pipeline_jobs
        }
        
        
        print(f"Validated jobs: {validate_pipeline_jobs}")
        if validate_pipeline_jobs:
            start(START_PIPELINES,payload)
        
    def import_source():
        GET_IMPORT_SOURCE_JOBS_URL = "https://datapipes.api.dev.aws.datapipes.cldcvr.dev/ingestor/v2/import/jobs?entity_type=SOURCE&page_size=300&offset_token="
        RUN_VALIDATE_SOURCE_URL = "https://datapipes.api.dev.aws.datapipes.cldcvr.dev/ingestor/v2/import/validate/source"
        START_SOURCE="https://datapipes.api.dev.aws.datapipes.cldcvr.dev/ingestor/v2/import/source/start"
        # Step 1: Call sync API
        trigger_id = call_sync_api(SYNC_API_URL)
        print(f"trigger_id: {trigger_id}")

        # Step 2: Check status until completed
        check_status(STATUS_API_URL,trigger_id)

        # Step 3: Get import jobs
        pipeline_jobs = get_import_jobs(GET_IMPORT_SOURCE_JOBS_URL)
        print(pipeline_jobs)
        # print(f"Retrieved {len(pipeline_jobs)} jobs to validate.")

        # Step 4: Run validate on each job
        
        source_import_ids = []
        for job in pipeline_jobs:
            print(f"pipeline_import_ids job: {job}")
            if not job["is_validated"] and not job["entity_created"]:
                source_import_ids.append(job["id"])
        
        payload=  {
            "force_update": True,
            "import_ids": source_import_ids
        }
        print(f"source_import_ids: {source_import_ids}")
        if source_import_ids:
            run_pipeline_validate(RUN_VALIDATE_SOURCE_URL,payload)
        
            running = set()
            while True:
                pipeline_jobs = get_import_jobs(GET_IMPORT_SOURCE_JOBS_URL)
                for job in pipeline_jobs:
                    print(f"job: {job}, {job['status']}")
                    if job["status"] in ["SUCCESS", "FAILED"] and job["id"] in source_import_ids:
                        running.add(job["id"])
                print(len(running),len(source_import_ids))
                if len(running) == len(source_import_ids):
                    break
                
                time.sleep(10)
        
        print("Validation completed.")
        validate_source_jobs = []
        pipeline_jobs = get_import_jobs(GET_IMPORT_SOURCE_JOBS_URL)
        for job in pipeline_jobs:
            if job["is_validated"] and not job["entity_created"]:
                validate_source_jobs.append(job["id"])
        
        payload ={
            "import_ids": validate_source_jobs
        }
        
        
        print(f"Validated jobs: {validate_source_jobs}")
        if validate_source_jobs:
            start(START_SOURCE,payload)
    
    import_source()
    import_pipelines()

def lambda_handler(event, context):
    main()
