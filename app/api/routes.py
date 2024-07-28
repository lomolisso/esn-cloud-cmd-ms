
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import gateway_cmd as gw_cmd_schemas
from app.api.schemas import sensor_cmd as s_cmd_schemas
from app.api.schemas import sensor_resp as s_resp_schemas
from app.api.utils import GatewayAPIHandler, store_response_in_redis, retrieve_response_from_redis
from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB

import redis

router = APIRouter()
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# --- Edge Gateway Commands ---
@router.post("/gateway/command/get/available-sensors", tags=["Edge Gateway Commands"], status_code=status.HTTP_202_ACCEPTED)
async def get_available_sensors(command: gw_cmd_schemas.GetAvailableSensors):
    """
    GET Available Sensors Command

    This command makes the gateway perform a BLE scan to discover the edge sensors available for provisioning.
    The results of the scan will be sent from the Gateway API on a separate endpoint once the scan is complete.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/gateway/command/get/available-sensors", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return [
        gw_cmd_schemas.BLEDevice(**device) for device in cmd_response.json()
    ]

@router.post("/gateway/command/get/provisioned-sensors", tags=["Edge Gateway Commands"], status_code=status.HTTP_202_ACCEPTED)
async def get_provisioned_sensors(command: gw_cmd_schemas.GetProvisionedSensors):
    """
    GET Provisioned Sensors Command

    This command makes the gateway retrieve the edge sensors that have been provisioned.
    The results of the provisioning will be sent from the Gateway API on a separate endpoint once the retrieval is complete.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/gateway/command/get/provisioned-sensors", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return [
        gw_cmd_schemas.BLEDevice(**device) for device in cmd_response.json()
    ]


@router.post("/gateway/command/add/provisioned-sensors", tags=["Edge Gateway Commands"], status_code=status.HTTP_202_ACCEPTED)
async def add_provisioned_sensors(command: gw_cmd_schemas.AddProvisionedSensors):
    """
    ADD Provisioned Sensors Command

    This command makes the gateway provision the edge sensors that were discovered during the BLE scan.
    The results of the provisioning will be sent to the gateway's metadata microservice for storage.
    The cloud can poll the metadata microservice to get the updated list of provisioned sensors.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/gateway/command/add/provisioned-sensors", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "ADD Provisioned Sensors Command Sent to Gateway API",
    }

@router.post("/gateway/command/add/registered-sensors", tags=["Edge Gateway Commands"], status_code=status.HTTP_202_ACCEPTED)
async def add_registered_sensors(command: gw_cmd_schemas.AddRegisteredSensors):
    """
    ADD Registered Sensors Command

    This command makes the gateway register the edge sensors that were provisioned.
    The results of the registration will be sent to the gateway's metadata microservice for storage.
    The cloud can poll the metadata microservice to get the updated list of registered sensors.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/gateway/command/add/registered-sensors", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "ADD Registered Sensors Command Sent to Gateway API",
    }


@router.post("/gateway/command/set/gateway-model", tags=["Edge Gateway Commands"], status_code=status.HTTP_202_ACCEPTED)
async def set_gateway_model(command: gw_cmd_schemas.SetGatewayModel):
    """
    SET Gateway Model Command

    This command makes the gateway upload a Machine Learning model to the gateway.
    The model will be stored in the gateway's filesystem and can be used for inference.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/gateway/command/set/gateway-model", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "SET Gateway Model Command Sent to Gateway API",
    }


# --- Edge Sensor Commands ---
@router.post("/sensor/command/set/sensor-state", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def set_sensor_state(command: s_cmd_schemas.SetSensorState):
    """
    SET Sensor State Command

    This command makes the sensor change it's state to either active or inactive.
    The sensor will only collect data and perform inference when it is in the active state.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/set/sensor-state", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "SET Sensor State Command Sent to Gateway API",
    }

@router.post("/sensor/command/get/sensor-state", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def command_get_sensor_state(command: s_cmd_schemas.GetSensorState):
    """
    GET Sensor State Command

    This command makes the sensor retrieve it's current state.
    The sensor will only collect data and perform inference when it is in the active state.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/get/sensor-state", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    command_uuids = cmd_response.json().get("command_uuids")

    return {
        "message": "GET Sensor State Command Sent to Gateway API",
        "command_uuids": command_uuids
    }

@router.post("/sensor/command/set/inference-layer", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def set_inference_layer(command: s_cmd_schemas.SetInferenceLayer):
    """
    SET Inference Layer Command

    This command makes the sensor switch it's inference layer to either the sensor, gateway or cloud.
    The sensor will perform inference on the selected layer.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/set/inference-layer", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "SET Inference Layer Command Sent to Gateway API",
    }

@router.post("/sensor/command/get/inference-layer", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def command_get_inference_layer(command: s_cmd_schemas.GetInferenceLayer):
    """
    GET Inference Layer Command

    This command makes the sensor retrieve it's current inference layer.
    The sensor will perform inference on the selected layer.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/get/inference-layer", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    command_uuids = cmd_response.json().get("command_uuids")

    return {
        "message": "GET Inference Layer Command Sent to Gateway API",
        "command_uuids": command_uuids
    }

@router.post("/sensor/command/set/sensor-config", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def set_sensor_config(command: s_cmd_schemas.SetSensorConfig):
    """
    SET Sensor Configuration Command

    This command makes the sensor update it's configuration.
    The sensor will use the new configuration for data collection and inference.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/set/sensor-config", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "SET Sensor Configuration Command Sent to Gateway API",
    }

@router.post("/sensor/command/get/sensor-config", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def command_get_sensor_config(command: s_cmd_schemas.GetSensorConfig):
    """
    GET Sensor Configuration Command

    This command makes the sensor retrieve it's current configuration.
    The sensor will use the configuration for data collection and inference.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/get/sensor-config", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    command_uuids = cmd_response.json().get("command_uuids")

    return {
        "message": "GET Sensor Configuration Command Sent to Gateway API",
        "command_uuids": command_uuids
    }

@router.post("/sensor/command/set/sensor-model", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def set_sensor_model(command: s_cmd_schemas.SetSensorModel):
    """
    SET Sensor Model Command

    This command makes the sensor upload a Machine Learning model to the sensor.
    The model will be stored in the sensor's filesystem and can be used for inference.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/set/sensor-model", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "SET Sensor Model Command Sent to Gateway API",
    }

@router.post("/sensor/command/set/inf-latency-bench", tags=["Edge Sensor Commands"], status_code=status.HTTP_202_ACCEPTED)
async def set_inf_latency_bench(command: s_cmd_schemas.InferenceLatencyBenchmarkCommand):
    """
    EXPERIMENTAL: SET Inference Latency Benchmark Command

    This command is for benchmarking the inference latency of the sensor.
    The command contains the reading UUID and the timestamp when the reading was sent.
    The sensor publishes an EXPORT once the command is received. The EXPORT contains
    the timestamp when the command was received and the latency calculated as the difference
    between the current timestamp and the timestamp in the command.
    """

    api_handler = GatewayAPIHandler(url=command.target.url)
    cmd_response = await api_handler.post_json(endpoint="/sensor/command/set/inf-latency-bench", data=command.model_dump())
    if cmd_response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=cmd_response.status_code, detail=cmd_response.json())
    
    return {
        "message": "SET Inference Latency Benchmark Command Sent to Gateway API",
    }


# --- Sensor Command Responses ---
@router.post("/store/sensor/response/get/sensor-state", tags=["Sensor Command Responses"], status_code=status.HTTP_201_CREATED)
async def store_get_sensor_state_response(response: s_resp_schemas.SensorStateResponse):
    """
    STORE Sensor State Command Response

    This endpoint is used to store the response of a GET Sensor State Command in the cache database.
    """

    # Retrieve the sensor name from the response
    command_uuid = response.metadata.command_uuid

    store_response_in_redis(
        redis_client=redis_client,
        command_uuid=command_uuid,
        response=response.model_dump()
    )

    return {
        "message": "GET Sensor State Command Response Stored in Cache Database"
    }

@router.post("/retrieve/sensor/response/get/sensor-state", tags=["Sensor Command Responses"], status_code=status.HTTP_200_OK)
async def retrieve_get_sensor_state_response(command_uuids: list[str]) -> list[s_resp_schemas.SensorStateResponse]:
    """
    RETRIEVE Sensor State Command Response

    This endpoint is used to retrieve the response of a GET Sensor State Command from the cache database.
    """

    responses = []
    for command_uuid in command_uuids:
        response = retrieve_response_from_redis(
            redis_client=redis_client,
            command_uuid=command_uuid
        )
        if response is None:
            continue
        responses.append(s_resp_schemas.SensorStateResponse(**response))

    return responses

@router.post("/store/sensor/response/get/inference-layer", tags=["Sensor Command Responses"], status_code=status.HTTP_201_CREATED)
async def store_get_inference_layer_response(response: s_resp_schemas.InferenceLayerResponse):
    """
    STORE Inference Layer Command Response

    This endpoint is used to store the response of a GET Inference Layer Command in the cache database.
    """

    # Retrieve the sensor name from the response
    command_uuid = response.metadata.command_uuid

    store_response_in_redis(
        redis_client=redis_client,
        command_uuid=command_uuid,
        response=response.model_dump()
    )

    return {
        "message": "GET Inference Layer Command Response Stored in Cache Database"
    }

@router.post("/retrieve/sensor/response/get/inference-layer", tags=["Sensor Command Responses"], status_code=status.HTTP_200_OK)
async def retrieve_get_inference_layer_response(command_uuids: list[str]) -> list[s_resp_schemas.InferenceLayerResponse]:
    """
    RETRIEVE Inference Layer Command Response

    This endpoint is used to retrieve the response of a GET Inference Layer Command from the cache database.
    """

    responses = []
    for command_uuid in command_uuids:
        response = retrieve_response_from_redis(
            redis_client=redis_client,
            command_uuid=command_uuid
        )
        if response is None:
            continue
        responses.append(s_resp_schemas.InferenceLayerResponse(**response))

    return responses

@router.post("/store/sensor/response/get/sensor-config", tags=["Sensor Command Responses"], status_code=status.HTTP_201_CREATED)
async def store_get_sensor_config_response(response: s_resp_schemas.SensorConfigResponse):
    """
    STORE Sensor Configuration Command Response

    This endpoint is used to store the response of a GET Sensor Configuration Command in the cache database.
    """

    # Retrieve the sensor name from the response
    command_uuid = response.metadata.command_uuid

    store_response_in_redis(
        redis_client=redis_client,
        command_uuid=command_uuid,
        response=response.model_dump()
    )

    return {
        "message": "GET Sensor Configuration Command Response Stored in Cache Database"
    }

@router.post("/retrieve/sensor/response/get/sensor-config", tags=["Sensor Command Responses"], status_code=status.HTTP_200_OK)
async def retrieve_get_sensor_config_response(command_uuids: list[str]) -> list[s_resp_schemas.SensorConfigResponse]:
    """
    RETRIEVE Sensor Configuration Command Response

    This endpoint is used to retrieve the response of a GET Sensor Configuration Command from the cache database.
    """

    responses = []
    for command_uuid in command_uuids:
        response = retrieve_response_from_redis(
            redis_client=redis_client,
            command_uuid=command_uuid
        )
        if response is None:
            continue
        responses.append(s_resp_schemas.SensorConfigResponse(**response))

    return responses
