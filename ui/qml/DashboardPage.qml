import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import "./components"

FluentPage {
    id: dashboardPage
    horizontalPadding: 24
    verticalPadding: 24

    // 欢迎横幅
    Item {
        id: headerItem
        width: parent.width
        height: 120

        Rectangle {
            anchors.fill: parent
            radius: 12
            gradient: Gradient {
                GradientStop {
                    position: 0.0
                    color: "#3b82f6"
                }
                GradientStop {
                    position: 1.0
                    color: "#1d4ed8"
                }
            }

            RowLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 20

                Column {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: qsTr("欢迎使用班级管理系统")
                        font.pixelSize: 24
                        font.bold: true
                        color: "white"
                    }

                    Text {
                        text: qsTr("高效管理您的班级和学生信息")
                        font.pixelSize: 14
                        color: "#e0e7ff"
                    }
                }

                // 快速操作按钮
                Row {
                    spacing: 12

                    Button {
                        text: qsTr("添加学生")
                        icon.name: "ic_fluent_person_add_20_regular"
                        onClicked: {
                            // 切换到学生管理页面
                            window.currentPageIndex = 1;
                        }
                    }

                    Button {
                        text: qsTr("创建班级")
                        icon.name: "ic_fluent_building_add_20_regular"
                        onClicked: {
                            // 切换到班级管理页面
                            window.currentPageIndex = 2;
                        }
                    }
                }
            }
        }
    }

    // 统计卡片网格
    GridLayout {
        width: parent.width
        columns: 4
        columnSpacing: 16
        rowSpacing: 16

        // 学生总数卡片
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            color: "white"
            radius: 8
            border.color: "#e5e7eb"
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 8

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: controller ? controller.totalStudents : "0"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#0078d4"  // Fluent Blue
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("学生总数")
                    font.pixelSize: 14
                    color: "#605e5c"  // Fluent Neutral
                }
            }
        }

        // 班级总数卡片
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            color: "white"
            radius: 8
            border.color: "#e5e7eb"
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 8

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: controller ? controller.totalClasses : "0"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#107c10"  // Fluent Green
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("班级总数")
                    font.pixelSize: 14
                    color: "#605e5c"  // Fluent Neutral
                }
            }
        }

        // 活跃班级卡片
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            color: "white"
            radius: 8
            border.color: "#e5e7eb"
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 8

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: controller ? controller.activeClasses : "0"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#f59e0b"
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("活跃班级")
                    font.pixelSize: 14
                    color: "#6b7280"
                }
            }
        }

        // 系统状态卡片
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            radius: 8
            color: "white"
            border.color: "#e5e7eb"
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 8

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 12
                    height: 12
                    radius: 6
                    color: "#10b981"
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("系统正常")
                    font.pixelSize: 14
                    color: "#6b7280"
                }
            }
        }
    }

    // 快速链接区域
    Rectangle {
        width: parent.width
        height: 200
        radius: 8
        color: "white"
        border.color: "#e5e7eb"
        border.width: 1

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            Text {
                text: qsTr("快速操作")
                font.pixelSize: 18
                font.bold: true
                color: "#1f2937"
            }

            GridLayout {
                width: parent.width
                columns: 3
                columnSpacing: 16
                rowSpacing: 12

                // 学生管理快捷方式
                Button {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: qsTr("学生管理")
                    icon.name: "ic_fluent_people_20_regular"
                    onClicked: window.currentPageIndex = 1
                }

                // 班级管理快捷方式
                Button {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: qsTr("班级管理")
                    icon.name: "ic_fluent_building_20_regular"
                    onClicked: window.currentPageIndex = 2
                }

                // 数据分析快捷方式
                Button {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: qsTr("数据分析")
                    icon.name: "ic_fluent_data_bar_vertical_20_regular"
                    onClicked: window.currentPageIndex = 3
                }
            }
        }
    }

    // 主内容区域
    mainContent: [
        ContentSection {
            sectionTitle: "数据概览"
            sectionSubtitle: "实时统计数据和趋势分析"

            content: [
                Row {
                    width: parent.width
                    spacing: 16

                    // 成绩趋势图表
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 300
                        color: "#ffffff"
                        radius: 12
                        border.color: "#e5e7eb"
                        border.width: 1

                        Column {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 16

                            Text {
                                text: "成绩趋势"
                                font.pixelSize: 16
                                font.weight: Font.Medium
                                color: "#111827"
                            }

                            Rectangle {
                                width: parent.width
                                height: parent.height - 40
                                color: "#f8fafc"
                                radius: 8

                                Text {
                                    text: "📈 图表区域"
                                    font.pixelSize: 24
                                    color: "#6b7280"
                                    anchors.centerIn: parent
                                }
                            }
                        }
                    }

                    // 班级排名
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 300
                        color: "#ffffff"
                        radius: 12
                        border.color: "#e5e7eb"
                        border.width: 1

                        Column {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 16

                            Text {
                                text: "班级排名"
                                font.pixelSize: 16
                                font.weight: Font.Medium
                                color: "#111827"
                            }

                            Column {
                                width: parent.width
                                spacing: 8

                                Repeater {
                                    model: 5

                                    Rectangle {
                                        width: parent.width
                                        height: 40
                                        color: "#f8fafc"
                                        radius: 8

                                        Row {
                                            anchors.fill: parent
                                            anchors.margins: 12
                                            spacing: 12

                                            Text {
                                                text: "#" + (index + 1)
                                                font.weight: Font.Medium
                                                color: "#3b82f6"
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Text {
                                                text: "高三" + (index + 1) + "班"
                                                color: "#111827"
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Item {
                                                Layout.fillWidth: true
                                            }

                                            Text {
                                                text: (85.5 - index * 2.1).toFixed(1)
                                                font.weight: Font.Medium
                                                color: "#10b981"
                                                anchors.verticalCenter: parent.verticalCenter
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        },
        ContentSection {
            sectionTitle: "最近活动"
            sectionSubtitle: "系统最新动态和重要通知"

            content: [
                Rectangle {
                    width: parent.width
                    height: 200
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Repeater {
                            model: 4

                            Row {
                                width: parent.width
                                spacing: 12

                                Rectangle {
                                    width: 8
                                    height: 8
                                    radius: 4
                                    color: ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"][index]
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Column {
                                    spacing: 2

                                    Text {
                                        text: ["新增学生张三", "高三1班成绩录入完成", "系统备份成功", "用户权限更新"][index]
                                        font.pixelSize: 14
                                        color: "#111827"
                                    }

                                    Text {
                                        text: ["2分钟前", "15分钟前", "1小时前", "3小时前"][index]
                                        font.pixelSize: 12
                                        color: "#6b7280"
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }
    ]

    // 对话框定义
    Dialog {
        id: addStudentDialog
        title: "添加学生"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 300

        Column {
            anchors.fill: parent
            spacing: 16

            TextField {
                width: parent.width
                placeholderText: "学生姓名"
            }

            TextField {
                width: parent.width
                placeholderText: "学号"
            }

            ComboBox {
                width: parent.width
                model: ["高一1班", "高一2班", "高二1班", "高二2班", "高三1班", "高三2班"]
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    Dialog {
        id: addClassDialog
        title: "创建班级"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 250

        Column {
            anchors.fill: parent
            spacing: 16

            TextField {
                id: classNameField
                width: parent.width
                placeholderText: "班级名称"
            }

            TextField {
                id: teacherNameField
                width: parent.width
                placeholderText: "班主任姓名"
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            if (classNameField.text && teacherNameField.text) {
                controller.addClass(classNameField.text, teacherNameField.text);
                classNameField.clear();
                teacherNameField.clear();
            }
        }
    }

    Dialog {
        id: importScoresDialog
        title: "导入成绩"
        modal: true
        anchors.centerIn: parent
        width: 500
        height: 300

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择要导入的成绩文件"
                font.pixelSize: 14
                color: "#374151"
            }

            Button {
                text: "选择文件"
                onClicked:
                // 文件选择逻辑
                {}
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }
}
