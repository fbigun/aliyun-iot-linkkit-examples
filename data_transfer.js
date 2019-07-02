var COMMAND_REPORT = 0x00;
var COMMAND_SET = 0x01;
var ALINK_PROP_REPORT_METHOD = 'thing.event.property.post'; //标准ALink JSON格式topic， 设备 上传属性数据到 云端
var ALINK_PROP_SET_METHOD = 'thing.service.property.set'; //标准ALink JSON格式topic， 云端 下发属性控制指令 到设备端
/*
示例数据：
传入参数 ->
    0x00002233441232013fa00000
输出结果 ->
    {"method":"thing.event.property.post","id":"2241348",
    "params":{"prop_float":1.25,"prop_int16":4658,"prop_bool":1},
    "version":"1.0"}
*/
function rawDataToProtocol(bytes) {
    var uint8Array = new Uint8Array(bytes.length);
    for (var i = 0; i < bytes.length; i++) {
        uint8Array[i] = bytes[i] & 0xff;
    }
    var dataView = new DataView(uint8Array.buffer, 0);
    var jsonMap = new Object();
    var fHead = uint8Array[0]; // command
    if (fHead == COMMAND_REPORT) {
        jsonMap['method'] = ALINK_PROP_REPORT_METHOD; //ALink JSON格式 - 属性上报topic
        jsonMap['version'] = '1.0'; //ALink JSON格式 - 协议版本号固定字段
        jsonMap['id'] = '' + dataView.getInt32(1); //ALink JSON格式 - 标示该次请求id值
        var params = {};
        params['prop_int16'] = dataView.getInt16(5); //对应产品属性中 prop_int16
        jsonMap['params'] = params; //ALink JSON格式 - params标准字段
    }
    return jsonMap;
    //return {"method": "thing.event.property.post","id": "1234567","params": {"prop_float": 1.11,"prop_int16": 1234,"prop_bool": 1},"version": "1.0"}
}
/*
示例数据：
传入参数 ->
    {"method":"thing.service.property.set","id":"12345","version":"1.0","params":{"prop_float":123.452, "prop_int16":333, "prop_bool":1}}
输出结果 ->
    0x0100003039014d0142f6e76d
*/
function protocolToRawData(json) {
    var method = json['method'];
    var id = json['id'];
    var version = json['version'];
    var payloadArray = [];
    if (method == ALINK_PROP_SET_METHOD) // 属性设置
    {
        var params = json['params'];
        var prop_float = params['prop_float'];
        var prop_int16 = params['prop_int16'];
        var prop_bool = params['prop_bool'];
        //按照自定义协议格式拼接 rawdata
        payloadArray = payloadArray.concat(buffer_uint8(COMMAND_SET)); // command字段
        payloadArray = payloadArray.concat(buffer_int32(parseInt(12345))); // ALink JSON格式 'id'
        payloadArray = payloadArray.concat(buffer_int16(prop_int16)); // 属性'prop_int16'的值
    } else {
        /* 回复上行的请求 */
        var code  = json['code'];
        payloadArray = payloadArray.concat(buffer_int16(code));  /* 填充payload的值 */
    }
    return payloadArray;
}
//以下是部分辅助函数
function buffer_uint8(value) {
    var uint8Array = new Uint8Array(1);
    var dv = new DataView(uint8Array.buffer, 0);
    dv.setUint8(0, value);
    return [].slice.call(uint8Array);
}
function buffer_int16(value) {
    var uint8Array = new Uint8Array(2);
    var dv = new DataView(uint8Array.buffer, 0);
    dv.setInt16(0, value);
    return [].slice.call(uint8Array);
}
function buffer_int32(value) {
    var uint8Array = new Uint8Array(4);
    var dv = new DataView(uint8Array.buffer, 0);
    dv.setInt32(0, value);
    return [].slice.call(uint8Array);
}
function buffer_float32(value) {
    var uint8Array = new Uint8Array(4);
    var dv = new DataView(uint8Array.buffer, 0);
    dv.setFloat32(0, value);
    return [].slice.call(uint8Array);
}