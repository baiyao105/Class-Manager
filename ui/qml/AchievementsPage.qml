import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

FluentPage {
    id: achievementsPage
    title: "成就系统"
    subtitle: "管理成就模板和学生成就记录"

    // 顶部分段控制器
    segmentedItems: [
        { text: "成就概览", value: "overview" },
        { text: "成就模板", value: "templates" },
        { text: "学生成就", value: "student_achievements" }
    ]

    property string currentSegment: "overview"

    onSegmentChanged: {
        currentSegment = value
    }

    // 状态卡片数据
    statusCards: [
        {
            title: "成就模板",
            value: "12",
            subtitle: "已创建",
            color: "#8b5cf6",
            icon: "🏆"
        },
        {
            title: "获得成就",
            value: "342",
            subtitle: "总计",
            color: "#f59e0b",
            icon: "⭐"
        },
        {
            title: "本月新增",
            value: "45",
            subtitle: "成就获得",
            color: "#10b981",
            icon: "📈"
        },
        {
            title: "活跃学生",
            value: "89",
            subtitle: "有成就记录",
            color: "#3b82f6",
            icon: "👥"
        }
    ]

    // 快速操作
    quickActions: [
        {
            text: "创建成就模板",
            icon: "ic_fluent_trophy_20_regular",
            onClicked: function() { createTemplateDialog.open() }
        },
        {
            text: "批量导入成就",
            icon: "ic_fluent_document_arrow_up_20_regular",
            onClicked: function() { importAchievementsDialog.open() }
        },
        {
            text: "导出成就报告",
            icon: "ic_fluent_document_arrow_down_20_regular",
            onClicked: function() { exportReport() }
        }
    ]

    // 主内容区域
    mainContent: [
        // 成就概览
        Column {
            width: parent.width
            spacing: 24
            visible: currentSegment === "overview"

            // 功能卡片
            GridLayout {
                width: parent.width
                columns: 3
                columnSpacing: 16
                rowSpacing: 16

                // 成就模板管理
                Rectangle {
                    Layout.preferredWidth: (parent.width - 32) / 3
                    Layout.preferredHeight: 200
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Row {
                            width: parent.width
                            spacing: 12

                            Text {
                                text: "🏆"
                                font.pixelSize: 32
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "成就模板"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: "#111827"
                                }

                                Text {
                                    text: "管理成就规则和条件"
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                }
                            }
                        }

                        Text {
                            text: "创建和编辑成就模板，设置触发条件和奖励规则。支持分数、考勤、行为等多种成就类型。"
                            font.pixelSize: 12
                            color: "#9ca3af"
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }

                        Button {
                            text: "管理模板"
                            highlighted: true
                            width: parent.width
                            onClicked: {
                                currentSegment = "templates"
                            }
                        }
                    }
                }

                // 学生成就查看
                Rectangle {
                    Layout.preferredWidth: (parent.width - 32) / 3
                    Layout.preferredHeight: 200
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Row {
                            width: parent.width
                            spacing: 12

                            Text {
                                text: "⭐"
                                font.pixelSize: 32
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "学生成就"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: "#111827"
                                }

                                Text {
                                    text: "查看学生获得的成就"
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                }
                            }
                        }

                        Text {
                            text: "浏览所有学生的成就记录，查看成就获得时间、条件和详细信息。"
                            font.pixelSize: 12
                            color: "#9ca3af"
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }

                        Button {
                            text: "查看成就"
                            width: parent.width
                            onClicked: {
                                currentSegment = "student_achievements"
                            }
                        }
                    }
                }

                // 成就统计分析
                Rectangle {
                    Layout.preferredWidth: (parent.width - 32) / 3
                    Layout.preferredHeight: 200
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Row {
                            width: parent.width
                            spacing: 12

                            Text {
                                text: "📊"
                                font.pixelSize: 32
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "成就统计"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: "#111827"
                                }

                                Text {
                                    text: "成就获得情况统计"
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                }
                            }
                        }

                        Text {
                            text: "分析成就获得趋势，查看最受欢迎的成就类型和学生参与度统计。"
                            font.pixelSize: 12
                            color: "#9ca3af"
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }

                        Button {
                            text: "查看统计"
                            flat: true
                            width: parent.width
                            onClicked: {
                                console.log("打开成就统计分析")
                            }
                        }
                    }
                }
            }

            // 最近获得的成就
            Rectangle {
                width: parent.width
                height: 320
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Row {
                        width: parent.width

                        Text {
                            text: "最近获得的成就"
                            font.pixelSize: 18
                            font.bold: true
                            color: "#111827"
                        }

                        Item { Layout.fillWidth: true }

                        Button {
                            text: "查看全部"
                            flat: true
                            onClicked: {
                                currentSegment = "student_achievements"
                            }
                        }
                    }

                    ListView {
                        width: parent.width
                        height: 240

                        model: [
                            { student: "张三", achievement: "学霸", time: "2024-01-15 14:30", level: "gold" },
                            { student: "李四", achievement: "全勤之星", time: "2024-01-15 09:00", level: "silver" },
                            { student: "王五", achievement: "助人为乐", time: "2024-01-14 16:45", level: "bronze" },
                            { student: "赵六", achievement: "进步之星", time: "2024-01-14 11:20", level: "silver" },
                            { student: "钱七", achievement: "初来乍到", time: "2024-01-13 08:15", level: "bronze" }
                        ]

                        delegate: Rectangle {
                            width: parent.width
                            height: 60
                            color: index % 2 === 0 ? "#f9fafb" : "transparent"
                            radius: 6

                            Row {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 16

                                // 成就等级图标
                                Rectangle {
                                    width: 36
                                    height: 36
                                    radius: 18
                                    color: modelData.level === "gold" ? "#fbbf24" :
                                           modelData.level === "silver" ? "#9ca3af" :
                                           "#cd7f32"
                                    anchors.verticalCenter: parent.verticalCenter

                                    Text {
                                        text: modelData.level === "gold" ? "🥇" :
                                              modelData.level === "silver" ? "🥈" : "🥉"
                                        anchors.centerIn: parent
                                        font.pixelSize: 16
                                    }
                                }

                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 4

                                    Text {
                                        text: modelData.student + " 获得了 " + modelData.achievement
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "#111827"
                                    }

                                    Text {
                                        text: modelData.time
                                        font.pixelSize: 12
                                        color: "#6b7280"
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                Button {
                                    text: "详情"
                                    flat: true
                                    font.pixelSize: 12
                                    anchors.verticalCenter: parent.verticalCenter
                                    onClicked: {
                                        console.log("查看成就详情:", modelData.achievement)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },

        // 成就模板管理
        Rectangle {
            width: parent.width
            height: 400
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1
            visible: currentSegment === "templates"

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16

                Text {
                    text: "成就模板管理"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "成就模板管理功能正在开发中..."
                    font.pixelSize: 14
                    color: "#6b7280"
                }
            }
        },

        // 学生成就查看
        Rectangle {
            width: parent.width
            height: 400
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1
            visible: currentSegment === "student_achievements"

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16

                Text {
                    text: "学生成就记录"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "学生成就查看功能正在开发中..."
                    font.pixelSize: 14
                    color: "#6b7280"
                }
            }
        }
    ]

    // 创建成就模板对话框
    Dialog {
        id: createTemplateDialog
        title: "创建成就模板"
        modal: true
        anchors.centerIn: parent
        width: 500
        height: 400

        Column {
            anchors.fill: parent
            spacing: 16

            TextField {
                width: parent.width
                placeholderText: "成就名称"
            }

            TextField {
                width: parent.width
                placeholderText: "成就描述"
            }

            ComboBox {
                width: parent.width
                model: ["学习成就", "行为成就", "考勤成就", "特殊成就"]
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 批量导入成就对话框
    Dialog {
        id: importAchievementsDialog
        title: "批量导入成就"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 300

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择要导入的成就数据文件"
                font.pixelSize: 14
                color: "#374151"
            }

            Button {
                text: "选择文件"
                width: parent.width
                onClicked: {
                    console.log("选择导入文件")
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 导出报告函数
    function exportReport() {
        console.log("导出成就报告")
    }
}
