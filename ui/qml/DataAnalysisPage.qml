import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

FluentPage {
    id: dataAnalysisPage
    horizontalPadding: 24
    verticalPadding: 24

    // 页面头部工具栏
    Item {
        id: headerItem
        width: parent.width
        height: 80

        Rectangle {
            anchors.fill: parent
            color: "white"
            radius: 8
            border.color: "#e5e7eb"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                Column {
                    Layout.fillWidth: true

                    Text {
                        text: qsTr("数据分析")
                        font.pixelSize: 20
                        font.bold: true
                        color: "#111827"
                    }

                    Text {
                        text: qsTr("深入分析学生成绩数据和学习趋势")
                        font.pixelSize: 14
                        color: "#6b7280"
                    }
                }

                // 导出报告按钮
                Button {
                    text: qsTr("导出报告")
                    icon.name: "ic_fluent_document_arrow_down_20_regular"
                }

                // 刷新数据按钮
                Button {
                    text: qsTr("刷新数据")
                    icon.name: "ic_fluent_arrow_clockwise_20_regular"
                    highlighted: true
                }
            }
        }
    }

    // 时间范围选择
    Rectangle {
        width: parent.width
        height: 80
        color: "#ffffff"
        radius: 12
        border.color: "#e5e7eb"

        Row {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            Text {
                text: "分析时间范围:"
                anchors.verticalCenter: parent.verticalCenter
                font.weight: Font.Medium
                color: "#374151"
            }

            ComboBox {
                id: timeRangeCombo
                model: ["本周", "本月", "本学期", "本学年", "自定义"]
                currentIndex: 2
                width: 120
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: "对比维度:"
                anchors.verticalCenter: parent.verticalCenter
                font.weight: Font.Medium
                color: "#374151"
            }

            ComboBox {
                id: dimensionCombo
                model: ["按班级", "按科目", "按学生", "按时间"]
                currentIndex: 0
                width: 120
                anchors.verticalCenter: parent.verticalCenter
            }

            Item {
                Layout.fillWidth: true
            }

            Text {
                text: "数据更新时间: 2024-01-15 14:30"
                color: "#6b7280"
                font.pixelSize: 12
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // 关键指标概览
    Row {
        width: parent.width
        spacing: 16

        StatCard {
            title: "班级平均分"
            value: "85.6"
            subtitle: "较上月 +2.3"
            icon: "📊"
            color: "#3b82f6"
            width: (parent.width - 48) / 4
        }

        StatCard {
            title: "最高分"
            value: "98"
            subtitle: "张三 - 数学"
            icon: "🏆"
            color: "#10b981"
            width: (parent.width - 48) / 4
        }

        StatCard {
            title: "及格率"
            value: "92%"
            subtitle: "较上月 +5%"
            icon: "✅"
            color: "#f59e0b"
            width: (parent.width - 48) / 4
        }

        StatCard {
            title: "进步学生"
            value: "15"
            subtitle: "分数提升 >5分"
            icon: "📈"
            color: "#8b5cf6"
            width: (parent.width - 48) / 4
        }
    }

    // 图表区域
    Row {
        width: parent.width
        spacing: 16

        // 成绩趋势图
        Rectangle {
            width: (parent.width - 16) * 0.6
            height: 400
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"

            Column {
                anchors.fill: parent
                anchors.margins: 20

                Row {
                    width: parent.width
                    Text {
                        text: "成绩趋势分析"
                        font.pixelSize: 18
                        font.weight: Font.Medium
                        color: "#111827"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    ComboBox {
                        model: ["全部科目", "语文", "数学", "英语", "物理", "化学"]
                        width: 120
                        height: 32
                    }
                }

                // 模拟图表区域
                Rectangle {
                    width: parent.width
                    height: parent.height - 60
                    color: "#f9fafb"
                    radius: 8
                    border.color: "#e5e7eb"

                    // 简单的折线图模拟
                    Canvas {
                        id: trendChart
                        anchors.fill: parent
                        anchors.margins: 20

                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.clearRect(0, 0, width, height);

                            // 绘制网格
                            ctx.strokeStyle = "#e5e7eb";
                            ctx.lineWidth = 1;

                            // 垂直网格线
                            for (var i = 0; i <= 6; i++) {
                                var x = (width / 6) * i;
                                ctx.beginPath();
                                ctx.moveTo(x, 0);
                                ctx.lineTo(x, height);
                                ctx.stroke();
                            }

                            // 水平网格线
                            for (var j = 0; j <= 4; j++) {
                                var y = (height / 4) * j;
                                ctx.beginPath();
                                ctx.moveTo(0, y);
                                ctx.lineTo(width, y);
                                ctx.stroke();
                            }

                            // 绘制趋势线
                            ctx.strokeStyle = "#3b82f6";
                            ctx.lineWidth = 3;
                            ctx.beginPath();

                            var points = [
                                {
                                    x: 0,
                                    y: height * 0.7
                                },
                                {
                                    x: width * 0.2,
                                    y: height * 0.6
                                },
                                {
                                    x: width * 0.4,
                                    y: height * 0.5
                                },
                                {
                                    x: width * 0.6,
                                    y: height * 0.4
                                },
                                {
                                    x: width * 0.8,
                                    y: height * 0.3
                                },
                                {
                                    x: width,
                                    y: height * 0.2
                                }
                            ];

                            ctx.moveTo(points[0].x, points[0].y);
                            for (var k = 1; k < points.length; k++) {
                                ctx.lineTo(points[k].x, points[k].y);
                            }
                            ctx.stroke();

                            // 绘制数据点
                            ctx.fillStyle = "#3b82f6";
                            for (var l = 0; l < points.length; l++) {
                                ctx.beginPath();
                                ctx.arc(points[l].x, points[l].y, 4, 0, 2 * Math.PI);
                                ctx.fill();
                            }
                        }
                    }

                    // 图例
                    Row {
                        anchors.bottom: parent.bottom
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottomMargin: 10
                        spacing: 20

                        Row {
                            spacing: 8
                            Rectangle {
                                width: 12
                                height: 12
                                color: "#3b82f6"
                                radius: 6
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "班级平均分"
                                font.pixelSize: 12
                                color: "#6b7280"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }
        }

        // 科目分布图
        Rectangle {
            width: (parent.width - 16) * 0.4
            height: 400
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"

            Column {
                anchors.fill: parent
                anchors.margins: 20

                Text {
                    text: "科目成绩分布"
                    font.pixelSize: 18
                    font.weight: Font.Medium
                    color: "#111827"
                }

                // 科目成绩条形图
                Column {
                    width: parent.width
                    spacing: 16
                    anchors.top: parent.top
                    anchors.topMargin: 40

                    Repeater {
                        model: [
                            {
                                subject: "数学",
                                score: 88,
                                color: "#3b82f6"
                            },
                            {
                                subject: "语文",
                                score: 85,
                                color: "#10b981"
                            },
                            {
                                subject: "英语",
                                score: 82,
                                color: "#f59e0b"
                            },
                            {
                                subject: "物理",
                                score: 79,
                                color: "#ef4444"
                            },
                            {
                                subject: "化学",
                                score: 86,
                                color: "#8b5cf6"
                            }
                        ]

                        Row {
                            width: parent.width
                            spacing: 12

                            Text {
                                text: modelData.subject
                                width: 50
                                font.pixelSize: 14
                                color: "#374151"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Rectangle {
                                width: (parent.width - 100) * (modelData.score / 100)
                                height: 20
                                color: modelData.color
                                radius: 10
                                anchors.verticalCenter: parent.verticalCenter

                                Behavior on width {
                                    NumberAnimation {
                                        duration: 800
                                        easing.type: Easing.OutCubic
                                    }
                                }
                            }

                            Text {
                                text: modelData.score
                                font.pixelSize: 14
                                font.weight: Font.Medium
                                color: "#111827"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }
        }
    }

    // 班级对比和排名
    Row {
        width: parent.width
        spacing: 16

        // 班级排名
        Rectangle {
            width: (parent.width - 16) / 2
            height: 350
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"

            Column {
                anchors.fill: parent
                anchors.margins: 20

                Text {
                    text: "班级排名"
                    font.pixelSize: 18
                    font.weight: Font.Medium
                    color: "#111827"
                }

                ListView {
                    width: parent.width
                    height: parent.height - 40
                    model: [
                        {
                            rank: 1,
                            class: "高一(3)班",
                            score: 88.5,
                            change: "+2"
                        },
                        {
                            rank: 2,
                            class: "高一(1)班",
                            score: 86.2,
                            change: "-1"
                        },
                        {
                            rank: 3,
                            class: "高一(2)班",
                            score: 84.8,
                            change: "+1"
                        },
                        {
                            rank: 4,
                            class: "高一(4)班",
                            score: 82.1,
                            change: "0"
                        },
                        {
                            rank: 5,
                            class: "高一(5)班",
                            score: 79.6,
                            change: "-2"
                        }
                    ]

                    delegate: Rectangle {
                        width: parent.width
                        height: 50
                        color: index % 2 === 0 ? "#f9fafb" : "transparent"
                        radius: 8

                        Row {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 16

                            // 排名
                            Rectangle {
                                width: 30
                                height: 30
                                radius: 15
                                color: {
                                    if (modelData.rank === 1)
                                        return "#fbbf24";
                                    if (modelData.rank === 2)
                                        return "#9ca3af";
                                    if (modelData.rank === 3)
                                        return "#cd7c2f";
                                    return "#e5e7eb";
                                }
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: modelData.rank
                                    anchors.centerIn: parent
                                    font.weight: Font.Bold
                                    color: modelData.rank <= 3 ? "#ffffff" : "#374151"
                                }
                            }

                            // 班级名称
                            Text {
                                text: modelData.class
                                font.pixelSize: 14
                                font.weight: Font.Medium
                                color: "#111827"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Item {
                                Layout.fillWidth: true
                            }

                            // 分数
                            Text {
                                text: modelData.score
                                font.pixelSize: 16
                                font.weight: Font.Bold
                                color: "#111827"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            // 变化
                            Rectangle {
                                width: 30
                                height: 20
                                radius: 10
                                color: {
                                    if (modelData.change.startsWith("+"))
                                        return "#dcfce7";
                                    if (modelData.change.startsWith("-"))
                                        return "#fee2e2";
                                    return "#f3f4f6";
                                }
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: modelData.change
                                    anchors.centerIn: parent
                                    font.pixelSize: 12
                                    color: {
                                        if (modelData.change.startsWith("+"))
                                            return "#166534";
                                        if (modelData.change.startsWith("-"))
                                            return "#dc2626";
                                        return "#6b7280";
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // 学习状态分析
        Rectangle {
            width: (parent.width - 16) / 2
            height: 350
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"

            Column {
                anchors.fill: parent
                anchors.margins: 20

                Text {
                    text: "学习状态分析"
                    font.pixelSize: 18
                    font.weight: Font.Medium
                    color: "#111827"
                }

                // 环形进度图模拟
                Rectangle {
                    width: parent.width
                    height: 200
                    color: "transparent"
                    anchors.horizontalCenter: parent.horizontalCenter

                    Column {
                        anchors.centerIn: parent
                        spacing: 20

                        // 优秀学生比例
                        Row {
                            spacing: 16
                            anchors.horizontalCenter: parent.horizontalCenter

                            Rectangle {
                                width: 60
                                height: 60
                                radius: 30
                                color: "#dcfce7"
                                border.color: "#10b981"
                                border.width: 4

                                Text {
                                    text: "68%"
                                    anchors.centerIn: parent
                                    font.pixelSize: 14
                                    font.weight: Font.Bold
                                    color: "#166534"
                                }
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                Text {
                                    text: "优秀学生"
                                    font.pixelSize: 14
                                    color: "#374151"
                                }
                                Text {
                                    text: "≥90分"
                                    font.pixelSize: 12
                                    color: "#6b7280"
                                }
                            }
                        }

                        // 良好学生比例
                        Row {
                            spacing: 16
                            anchors.horizontalCenter: parent.horizontalCenter

                            Rectangle {
                                width: 60
                                height: 60
                                radius: 30
                                color: "#dbeafe"
                                border.color: "#3b82f6"
                                border.width: 4

                                Text {
                                    text: "24%"
                                    anchors.centerIn: parent
                                    font.pixelSize: 14
                                    font.weight: Font.Bold
                                    color: "#1d4ed8"
                                }
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                Text {
                                    text: "良好学生"
                                    font.pixelSize: 14
                                    color: "#374151"
                                }
                                Text {
                                    text: "80-89分"
                                    font.pixelSize: 12
                                    color: "#6b7280"
                                }
                            }
                        }

                        // 需要关注
                        Row {
                            spacing: 16
                            anchors.horizontalCenter: parent.horizontalCenter

                            Rectangle {
                                width: 60
                                height: 60
                                radius: 30
                                color: "#fee2e2"
                                border.color: "#ef4444"
                                border.width: 4

                                Text {
                                    text: "8%"
                                    anchors.centerIn: parent
                                    font.pixelSize: 14
                                    font.weight: Font.Bold
                                    color: "#dc2626"
                                }
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                Text {
                                    text: "需要关注"
                                    font.pixelSize: 14
                                    color: "#374151"
                                }
                                Text {
                                    text: "<70分"
                                    font.pixelSize: 12
                                    color: "#6b7280"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 详细分析报告
    Rectangle {
        width: parent.width
        height: 300
        color: "#ffffff"
        radius: 12
        border.color: "#e5e7eb"

        Column {
            anchors.fill: parent
            anchors.margins: 20

            Text {
                text: "智能分析报告"
                font.pixelSize: 18
                font.weight: Font.Medium
                color: "#111827"
            }

            ScrollView {
                width: parent.width
                height: parent.height - 40
                clip: true

                Column {
                    width: parent.width
                    spacing: 16

                    // 分析要点
                    Repeater {
                        model: [
                            {
                                type: "positive",
                                title: "整体表现良好",
                                content: "本月班级平均分为85.6分，较上月提升2.3分，整体学习状态呈上升趋势。"
                            },
                            {
                                type: "warning",
                                title: "数学科目需要关注",
                                content: "数学科目平均分为79分，低于其他科目，建议加强数学基础训练和个别辅导。"
                            },
                            {
                                type: "info",
                                title: "优秀学生分布",
                                content: "68%的学生成绩优秀(≥90分)，24%的学生成绩良好(80-89分)，学习氛围积极向上。"
                            },
                            {
                                type: "suggestion",
                                title: "改进建议",
                                content: "建议针对8%需要关注的学生制定个性化学习计划，加强基础知识巩固。"
                            }
                        ]

                        Rectangle {
                            width: parent.width
                            height: 60
                            color: {
                                switch (modelData.type) {
                                case "positive":
                                    return "#dcfce7";
                                case "warning":
                                    return "#fef3c7";
                                case "info":
                                    return "#dbeafe";
                                case "suggestion":
                                    return "#f3e8ff";
                                default:
                                    return "#f9fafb";
                                }
                            }
                            radius: 8
                            border.color: {
                                switch (modelData.type) {
                                case "positive":
                                    return "#10b981";
                                case "warning":
                                    return "#f59e0b";
                                case "info":
                                    return "#3b82f6";
                                case "suggestion":
                                    return "#8b5cf6";
                                default:
                                    return "#e5e7eb";
                                }
                            }
                            border.width: 1

                            Row {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12

                                Text {
                                    text: {
                                        switch (modelData.type) {
                                        case "positive":
                                            return "✅";
                                        case "warning":
                                            return "⚠️";
                                        case "info":
                                            return "ℹ️";
                                        case "suggestion":
                                            return "💡";
                                        default:
                                            return "📊";
                                        }
                                    }
                                    font.pixelSize: 20
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 4

                                    Text {
                                        text: modelData.title
                                        font.pixelSize: 14
                                        font.weight: Font.Medium
                                        color: "#111827"
                                    }

                                    Text {
                                        text: modelData.content
                                        font.pixelSize: 12
                                        color: "#6b7280"
                                        wrapMode: Text.WordWrap
                                        width: parent.parent.width - 60
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
