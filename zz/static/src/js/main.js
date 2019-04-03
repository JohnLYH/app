odoo.define('zz.echart_action', function (require) {
    'use strict';
    var core = require('web.core');
    var Widget = require('web.Widget');
    var WebClient = require('web.WebClient');

    WebClient.include({
        // action_manager在执行完一个动作后（done...）会触发：
        // self.trigger_up('current_action_updated', {action: new_action});
        // echart的初始化参数必须要是可见元素，执行客户端动作时元素未添加到DOM树中，必须等到动作执行完成才可以初始化echart报表
        // 选择复写current_action_updated方法来保证渲染是在元素可见之后执行
        current_action_updated: function (action) {
            this._super.apply(this, arguments);
            //     // action 中保存了动作关联的widget, 在widget中可以通过willStart来获取数据并存储到widget中
            //     // Note that at this point, the widget does not have a DOM root element.
            //     // The willStart hook is mostly useful to perfom some asynchronous work, such as fetching data from the server
            var action_descr = action && action.action_descr;
            var tag = action_descr && action_descr.tag;

            if (tag === 'echart_action') {
                var option = {
                    tooltip: {
                        show: true
                    },
                    xAxis: [{
                        type: 'category',
                        data: ["老王", "老张", "老李", "老头"]
                    }],
                    yAxis: [{
                        type: 'value'
                    }],
                    series: [{
                        "name": "年龄",
                        "type": "bar",
                        "data": [40, 50, 47, 66]
                    }]
                };
                var myChart = echarts.init(document.getElementById('ediv'));
                myChart.setOption(option);
            }
        }
    });
    // id为echartAction的前端QWeb模板在static/src/xml中定义
    var EchartAction = Widget.extend({template: 'echartAction'});
    // 注册echart_action这个客户端动作
    core.action_registry.add("echart_action", EchartAction);
});