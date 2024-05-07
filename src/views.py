from datetime import datetime

from flask import jsonify, Blueprint, request
from flask_parameter_validation import ValidateParameters, Query

from utils.penman_monteith import PenmanMonteithET0
from exceptions import BaseError, ParameterError
from settings import IRRIGATION_MODES

v1 = Blueprint('v1', __name__)


@v1.errorhandler(BaseError)
def all_exception_handler(error):
    return jsonify({"error": error.value})


@v1.route("/irrigation-decision", methods=['GET',])
@ValidateParameters()
# pylint: disable=too-many-arguments
def irrigation_decision(
        # 在此处的参数都是required的
        latitude: float = Query(min_int=-90, max_int=90),
        longitude: float = Query(min_int=-180, max_int=180),
        altitude: float = Query(),
        forecast_start_time: datetime = Query(datetime_format='%Y-%m-%d'),
        forecast_end_time: datetime = Query(datetime_format='%Y-%m-%d'),
        crop: str = Query()
    ):
    """
    灌溉算法接口

    用户传入地点、作物种类、灌溉模式、播种时间、人为灌溉（可选）、关键生育节点（可选），得到预测的灌溉时间、灌溉量，主要通过彭曼方程结合预测气象通过水量平衡进行灌溉决策

    :param forecast_start_time: 预报开始日期，必须
    :type forecast_start_time:date
    :param forecast_end_time: 预报结束日期， 必须
    :type forecast_end_time:date
    :param latitude: 该位置点的纬度， 必须 （注：目前必须，未来可能会根据经纬度自动获取）
    :type latitude:float
    :param longitude: 该位置点的经度，必须
    :type longitude:float
    :param altitude: 该位置点的高度，必须
    :type altitude:float
    :param crop: 作物名称，必须
    :type crop:string
    :param irrigation_mode: 灌溉模式，必须, 可选项为 'drip', 'sprinkler', 'flood'
    :type irrigation_mode:string
    :return:
    成功：返回计算出的灌溉决策数据， 如：

    [["Date","Actual irrigation amount","Irr_Duration"],
    ["05-18",31.95125821118531,4.790293584885353],
    ["06-10",32.31726916880375,4.845167791424849]]


    失败：返回失败原因, 如：

    {
        "error": "Missing required query parameter 'latitude'."
    }
    """
    # ↑ 注意：上面的注释会被用来生成api doc

    # 纬度, 经度, 海拔高度
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    altitude = request.args.get('altitude')
    forecast_start_time = datetime.strptime(request.args.get('forecast_start_time'), '%Y-%m-%d')
    forecast_end_time = datetime.strptime(request.args.get('forecast_end_time'), '%Y-%m-%d')
    crop = request.args.get('crop')
    irrigation_mode = request.args.get('irrigation_mode')

    if crop != 'cotton':
        raise ParameterError('Error, `crop` can only be `cotton` at present!')

    if irrigation_mode not in IRRIGATION_MODES.keys():
        raise ParameterError(f"Error, `irrigation_mode` can only be one of `{ ', '.join(IRRIGATION_MODES.keys()) }` !")

    pm = PenmanMonteithET0(forecast_start_time, forecast_end_time, latitude, longitude, altitude)
    df = pm.generate_crop_irrigation_decision_report(crop)

    # header = ['Date', 'Irrigation', 'Irrigation Amount', 'Actual irrigation amount', 'Irr_Duration', 'Irrigation_Period']
    header = ['Date', 'Actual irrigation amount', 'Irr_Duration']
    result = [header,]
    result.extend(df[header].values[df['Irr_Duration'].values != 0].tolist())
    return jsonify(result)
