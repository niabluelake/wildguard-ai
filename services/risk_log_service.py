from services.db_service import execute


def save_risk_prediction_log(input_data, prediction_result):
    query = """
        INSERT INTO risk_prediction_log (
            day,
            camera_type,
            weather,
            location,
            time_zone,
            season,
            object_count,
            max_bbox_area_ratio,
            avg_bbox_area_ratio,
            risk_level,
            risk_message
        ) VALUES (
            :day,
            :camera_type,
            :weather,
            :location,
            :time_zone,
            :season,
            :object_count,
            :max_bbox_area_ratio,
            :avg_bbox_area_ratio,
            :risk_level,
            :risk_message
        )
    """

    params = {
        "day": input_data.get("day"),
        "camera_type": input_data.get("camera_type"),
        "weather": input_data.get("weather"),
        "location": input_data.get("location"),
        "time_zone": input_data.get("time_zone"),
        "season": input_data.get("season"),
        "object_count": input_data.get("object_count"),
        "max_bbox_area_ratio": input_data.get("max_bbox_area_ratio"),
        "avg_bbox_area_ratio": input_data.get("avg_bbox_area_ratio"),
        "risk_level": prediction_result.get("risk_level"),
        "risk_message": prediction_result.get("message"),
    }

    return execute(query, params)
