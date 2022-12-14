from flask import Blueprint, request

from homecontrol.api.helpers import (
    apply_filters,
    authenticated,
    response,
    response_message,
)
from homecontrol.helpers import ResponseStatus
from homecontrol.hue.exceptions import HueAPIError
from homecontrol.hue.grouped_light import GroupedLightState
from homecontrol.hue.manager import HueManager


hue_api = Blueprint("hue_api", __name__)

# ACManager
device_manager = HueManager()


@hue_api.route("/hue/<bridge_name>/rooms", methods=["GET"])
@authenticated
def get_rooms(bridge_name):
    """
    Returns a dictionary of rooms a bridge has access to
    """
    bridge = device_manager.get_bridge(bridge_name)
    with bridge.start_session() as conn:
        try:
            rooms = conn.room.get_rooms()
            rooms = apply_filters(rooms)

            return response(rooms, ResponseStatus.OK)
        except HueAPIError as err:
            return response_message(str(err), ResponseStatus.BAD_REQUEST)


@hue_api.route("/hue/<bridge_name>/grouped_lights/<group_id>", methods=["GET"])
@authenticated
def get_grouped_light_state(bridge_name, group_id):
    """
    Returns the current state of a group of lights
    """
    bridge = device_manager.get_bridge(bridge_name)
    with bridge.start_session() as conn:
        try:
            return response(
                conn.grouped_light.get_state(group_id).to_dict(), ResponseStatus.OK
            )
        except HueAPIError as err:
            return response_message(str(err), ResponseStatus.BAD_REQUEST)


@hue_api.route("/hue/<bridge_name>/grouped_lights/<group_id>", methods=["PUT"])
@authenticated
def set_grouped_light_state(bridge_name, group_id):
    """
    Updates the state of a group of lights
    """
    payload = request.get_json()
    bridge = device_manager.get_bridge(bridge_name)
    state = GroupedLightState.from_dict(payload)
    with bridge.start_session() as conn:
        try:
            conn.grouped_light.set_state(group_id, state)

            return response("Success", ResponseStatus.OK)
        except HueAPIError as err:
            return response_message(str(err), ResponseStatus.BAD_REQUEST)


@hue_api.route("/hue/<bridge_name>/scenes", methods=["GET"])
@authenticated
def get_scenes(bridge_name):
    """
    Returns a list of scenes a bridge has access to
    """

    bridge = device_manager.get_bridge(bridge_name)
    with bridge.start_session() as conn:
        try:
            scenes = conn.scene.get_scenes()
            scenes = apply_filters(scenes)

            return response(scenes, ResponseStatus.OK)
        except HueAPIError as err:
            return response_message(str(err), ResponseStatus.BAD_REQUEST)


@hue_api.route("/hue/<bridge_name>/scenes/<scene_id>", methods=["PUT"])
@authenticated
def recall_scene(bridge_name, scene_id):
    """
    Recalls a scene
    """
    bridge = device_manager.get_bridge(bridge_name)
    with bridge.start_session() as conn:
        try:
            conn.scene.recall_scene(scene_id)

            return response("Success", ResponseStatus.OK)
        except HueAPIError as err:
            return response_message(str(err), ResponseStatus.BAD_REQUEST)
