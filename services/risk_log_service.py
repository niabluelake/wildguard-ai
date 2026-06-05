from services.db_service import execute, fetch_all


def save_risk_prediction_log(
    user_id,
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
    risk_message,
):
    query = """
        INSERT INTO risk_prediction_log (
            user_id,
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
            :user_id,
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
        "user_id": user_id,
        "day": day,
        "camera_type": camera_type,
        "weather": weather,
        "location": location,
        "time_zone": time_zone,
        "season": season,
        "object_count": object_count,
        "max_bbox_area_ratio": max_bbox_area_ratio,
        "avg_bbox_area_ratio": avg_bbox_area_ratio,
        "risk_level": risk_level,
        "risk_message": risk_message,
    }

    return execute(query, params)


def get_recent_risk_logs(limit=50):
    sql = """
        SELECT
            log_id,
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
            risk_message,
            created_at
        FROM risk_prediction_log
        ORDER BY log_id DESC
        FETCH FIRST :limit ROWS ONLY
    """

    return fetch_all(sql, {"limit": limit})
