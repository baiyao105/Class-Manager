import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: importExportPage

    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24

        // 页面标题
        Row {
            width: parent.width
            spacing: 16

            Column {
                Text {
                    text: "导入导出"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "批量导入导出学生信息、成绩数据和班级资料"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }

            Item {
                Layout.fillWidth: true
            }

            Row {
                spacing: 12
                anchors.verticalCenter: parent.verticalCenter

                Button {
                    text: "操作历史"
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E"
                }

                Button {
                    text: "帮助文档"
                    highlighted: true
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z'/%3E%3C/svg%3E"
                }
            }
        }

        // 快速操作卡片
        Row {
            width: parent.width
            spacing: 16

            // 导入数据
            Rectangle {
                width: (parent.width - 32) / 3
                height: 200
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Row {
                        spacing: 12

                        Rectangle {
                            width: 40
                            height: 40
                            radius: 8
                            color: "#dbeafe"

                            Text {
                                text: "📥"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "导入数据"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "批量导入学生和成绩"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "导入学生信息"
                            width: parent.width
                            onClicked: importStudentsDialog.open()
                        }

                        Button {
                            text: "导入成绩数据"
                            width: parent.width
                            onClicked: importScoresDialog.open()
                        }

                        Button {
                            text: "导入班级信息"
                            width: parent.width
                            onClicked: importClassesDialog.open()
                        }
                    }
                }
            }

            // 导出数据
            Rectangle {
                width: (parent.width - 32) / 3
                height: 200
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Row {
                        spacing: 12

                        Rectangle {
                            width: 40
                            height: 40
                            radius: 8
                            color: "#dcfce7"

                            Text {
                                text: "📤"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "导出数据"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "导出各类报表和数据"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "导出学生名单"
                            width: parent.width
                            onClicked: exportStudentsDialog.open()
                        }

                        Button {
                            text: "导出成绩报表"
                            width: parent.width
                            onClicked: exportScoresDialog.open()
                        }

                        Button {
                            text: "导出统计分析"
                            width: parent.width
                            onClicked: exportAnalysisDialog.open()
                        }
                    }
                }
            }

            // 模板下载
            Rectangle {
                width: (parent.width - 32) / 3
                height: 200
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Row {
                        spacing: 12

                        Rectangle {
                            width: 40
                            height: 40
                            radius: 8
                            color: "#fef3c7"

                            Text {
                                text: "📋"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "模板下载"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "下载标准导入模板"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "学生信息模板"
                            width: parent.width
                        }

                        Button {
                            text: "成绩录入模板"
                            width: parent.width
                        }

                        Button {
                            text: "班级信息模板"
                            width: parent.width
                        }
                    }
                }
            }
        }

        // 导入导出历史
        Rectangle {
            width: parent.width
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
                        text: "操作历史"
                        font.pixelSize: 18
                        font.weight: Font.Medium
                        color: "#111827"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: "清空历史"
                        height: 32
                        background: Rectangle {
                            color: parent.hovered ? "#fee2e2" : "transparent"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "#dc2626"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }

                // 历史记录表格
                Rectangle {
                    width: parent.width
                    height: parent.height - 60
                    color: "#f9fafb"
                    radius: 8
                    border.color: "#e5e7eb"

                    Column {
                        anchors.fill: parent

                        // 表头
                        Rectangle {
                            width: parent.width
                            height: 40
                            color: "#f3f4f6"
                            radius: 8

                            Row {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 0

                                Text {
                                    text: "操作时间"
                                    width: 120
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "操作类型"
                                    width: 100
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "数据类型"
                                    width: 100
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "文件名"
                                    width: 200
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "状态"
                                    width: 80
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "记录数"
                                    width: 80
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "操作"
                                    Layout.fillWidth: true
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }
                        }

                        // 历史记录列表
                        ScrollView {
                            width: parent.width
                            height: parent.height - 40
                            clip: true

                            ListView {
                                model: [
                                    {
                                        time: "2024-01-15 14:30",
                                        type: "导入",
                                        dataType: "学生信息",
                                        fileName: "students_2024_spring.xlsx",
                                        status: "成功",
                                        count: 45
                                    },
                                    {
                                        time: "2024-01-15 10:15",
                                        type: "导出",
                                        dataType: "成绩报表",
                                        fileName: "scores_report_jan.xlsx",
                                        status: "成功",
                                        count: 1250
                                    },
                                    {
                                        time: "2024-01-14 16:45",
                                        type: "导入",
                                        dataType: "成绩数据",
                                        fileName: "math_scores.csv",
                                        status: "失败",
                                        count: 0
                                    },
                                    {
                                        time: "2024-01-14 09:20",
                                        type: "导出",
                                        dataType: "学生名单",
                                        fileName: "class_roster.pdf",
                                        status: "成功",
                                        count: 42
                                    },
                                    {
                                        time: "2024-01-13 15:30",
                                        type: "导入",
                                        dataType: "班级信息",
                                        fileName: "class_info.xlsx",
                                        status: "成功",
                                        count: 5
                                    }
                                ]

                                delegate: Rectangle {
                                    width: parent.width
                                    height: 50
                                    color: index % 2 === 0 ? "#ffffff" : "#f9fafb"

                                    Row {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 0

                                        Text {
                                            text: modelData.time
                                            width: 120
                                            font.pixelSize: 12
                                            color: "#6b7280"
                                            anchors.verticalCenter: parent.verticalCenter
                                        }

                                        Rectangle {
                                            width: 100
                                            height: parent.height
                                            color: "transparent"
                                            anchors.verticalCenter: parent.verticalCenter

                                            Rectangle {
                                                width: 50
                                                height: 24
                                                radius: 12
                                                color: modelData.type === "导入" ? "#dbeafe" : "#dcfce7"
                                                anchors.centerIn: parent

                                                Text {
                                                    text: modelData.type
                                                    anchors.centerIn: parent
                                                    font.pixelSize: 12
                                                    color: modelData.type === "导入" ? "#1d4ed8" : "#166534"
                                                }
                                            }
                                        }

                                        Text {
                                            text: modelData.dataType
                                            width: 100
                                            font.pixelSize: 12
                                            color: "#374151"
                                            anchors.verticalCenter: parent.verticalCenter
                                        }

                                        Text {
                                            text: modelData.fileName
                                            width: 200
                                            font.pixelSize: 12
                                            color: "#111827"
                                            anchors.verticalCenter: parent.verticalCenter
                                            elide: Text.ElideRight
                                        }

                                        Rectangle {
                                            width: 80
                                            height: parent.height
                                            color: "transparent"
                                            anchors.verticalCenter: parent.verticalCenter

                                            Rectangle {
                                                width: 50
                                                height: 24
                                                radius: 12
                                                color: modelData.status === "成功" ? "#dcfce7" : "#fee2e2"
                                                anchors.centerIn: parent

                                                Text {
                                                    text: modelData.status
                                                    anchors.centerIn: parent
                                                    font.pixelSize: 12
                                                    color: modelData.status === "成功" ? "#166534" : "#dc2626"
                                                }
                                            }
                                        }

                                        Text {
                                            text: modelData.count
                                            width: 80
                                            font.pixelSize: 12
                                            color: "#6b7280"
                                            anchors.verticalCenter: parent.verticalCenter
                                        }

                                        Row {
                                            Layout.fillWidth: true
                                            spacing: 8
                                            anchors.verticalCenter: parent.verticalCenter

                                            Button {
                                                text: "详情"
                                                height: 28
                                                width: 50
                                                font.pixelSize: 12
                                            }

                                            Button {
                                                text: "重试"
                                                height: 28
                                                width: 50
                                                font.pixelSize: 12
                                                visible: modelData.status === "失败"
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
    }

    // 导入学生信息对话框
    Dialog {
        id: importStudentsDialog
        title: "导入学生信息"
        width: 600
        height: 500
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "支持 Excel (.xlsx) 和 CSV (.csv) 格式文件"
                color: "#6b7280"
            }

            // 文件选择区域
            Rectangle {
                width: parent.width
                height: 150
                color: "#f9fafb"
                border.color: "#d1d5db"
                border.width: 2
                // 移除不支持的border.style属性
                radius: 8

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    Text {
                        text: "📁"
                        font.pixelSize: 48
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "拖拽文件到此处或点击选择文件"
                        color: "#6b7280"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Button {
                        text: "选择文件"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            // 导入选项
            Column {
                width: parent.width
                spacing: 12

                Text {
                    text: "导入选项"
                    font.weight: Font.Medium
                    color: "#374151"
                }

                CheckBox {
                    text: "跳过重复学号的记录"
                    checked: true
                }

                CheckBox {
                    text: "自动生成缺失的学号"
                    checked: false
                }

                CheckBox {
                    text: "导入后发送通知"
                    checked: true
                }
            }

            // 字段映射
            Text {
                text: "字段映射 (拖拽调整顺序)"
                font.weight: Font.Medium
                color: "#374151"
            }

            Row {
                width: parent.width
                spacing: 16

                Column {
                    width: (parent.width - 16) / 2
                    Text {
                        text: "Excel列"
                        font.pixelSize: 12
                        color: "#6b7280"
                    }
                    Rectangle {
                        width: parent.width
                        height: 100
                        color: "#f3f4f6"
                        radius: 4
                        border.color: "#d1d5db"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4

                            Text {
                                text: "A: 学号"
                                font.pixelSize: 12
                            }
                            Text {
                                text: "B: 姓名"
                                font.pixelSize: 12
                            }
                            Text {
                                text: "C: 性别"
                                font.pixelSize: 12
                            }
                            Text {
                                text: "D: 班级"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                Column {
                    width: (parent.width - 16) / 2
                    Text {
                        text: "系统字段"
                        font.pixelSize: 12
                        color: "#6b7280"
                    }
                    Rectangle {
                        width: parent.width
                        height: 100
                        color: "#f3f4f6"
                        radius: 4
                        border.color: "#d1d5db"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4

                            Text {
                                text: "student_id"
                                font.pixelSize: 12
                            }
                            Text {
                                text: "name"
                                font.pixelSize: 12
                            }
                            Text {
                                text: "gender"
                                font.pixelSize: 12
                            }
                            Text {
                                text: "class_name"
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 其他对话框类似结构...
    Dialog {
        id: importScoresDialog
        title: "导入成绩数据"
        width: 600
        height: 500
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    Dialog {
        id: importClassesDialog
        title: "导入班级信息"
        width: 600
        height: 500
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    Dialog {
        id: exportStudentsDialog
        title: "导出学生名单"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    Dialog {
        id: exportScoresDialog
        title: "导出成绩报表"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    Dialog {
        id: exportAnalysisDialog
        title: "导出统计分析"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }
}
