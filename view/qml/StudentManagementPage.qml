import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id: studentManagementPage
    horizontalPadding: 0
    verticalPadding: 0

    // 主容器
    Rectangle {
        anchors.fill: parent
        color: "#f8fafc"
        border.width: 1
        border.color: "#e2e8f0"
        radius: 8

        Column {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 24

            // 顶部分段控制器
            Rectangle {
                width: parent.width
                height: 60
                color: "#ffffff"
                radius: 12
                border.width: 1
                border.color: "#e2e8f0"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    // 页面标题
                    Column {
                        Layout.fillWidth: true

                        Text {
                            text: "学生管理"
                            font.pixelSize: 20
                            font.weight: Font.DemiBold
                            color: "#1e293b"
                        }

                        Text {
                            text: "管理学生信息，支持批量操作"
                            font.pixelSize: 14
                            color: "#64748b"
                        }
                    }

                    // 操作按钮组
                    Row {
                        spacing: 12

                        Button {
                            text: "添加学生"
                            highlighted: true
                            height: 36
                            onClicked: addStudentDialog.open()
                        }

                        Button {
                            text: "批量导入"
                            height: 36
                            onClicked: importStudentsDialog.open()
                        }

                        Button {
                            text: "导出数据"
                            height: 36
                            onClicked: exportStudentsDialog.open()
                        }
                    }
                }
            }

            // 主要布局区域
            Rectangle {
                width: parent.width
                height: parent.height - 108 // 减去顶部和底部的高度
                color: "transparent"

                RowLayout {
                    anchors.fill: parent
                    spacing: 16

                    // 左侧工作区
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#ffffff"
                        radius: 12
                        border.width: 1
                        border.color: "#e2e8f0"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 16

                            // 统计卡片区域
                            GridLayout {
                                width: parent.width
                                columns: 4
                                columnSpacing: 16
                                rowSpacing: 16

                                Repeater {
                                    model: [
                                        {
                                            title: "学生总数",
                                            value: "156",
                                            subtitle: "本学期新增 12 人",
                                            icon: "👥",
                                            color: "#3b82f6"
                                        },
                                        {
                                            title: "男生人数",
                                            value: "82",
                                            subtitle: "占比 52.6%",
                                            icon: "👦",
                                            color: "#10b981"
                                        },
                                        {
                                            title: "女生人数",
                                            value: "74",
                                            subtitle: "占比 47.4%",
                                            icon: "👧",
                                            color: "#f59e0b"
                                        },
                                        {
                                            title: "平均年龄",
                                            value: "16.8",
                                            subtitle: "年龄范围 15-18",
                                            icon: "📊",
                                            color: "#8b5cf6"
                                        }
                                    ]

                                    Rectangle {
                                        Layout.preferredWidth: (parent.width - 48) / 4
                                        Layout.preferredHeight: 100
                                        color: "#ffffff"
                                        radius: 8
                                        border.width: 1
                                        border.color: "#e2e8f0"

                                        MouseArea {
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: parent.color = "#f8fafc"
                                            onExited: parent.color = "#ffffff"
                                        }

                                        Column {
                                            anchors.centerIn: parent
                                            spacing: 4

                                            Text {
                                                text: modelData.icon
                                                font.pixelSize: 24
                                                anchors.horizontalCenter: parent.horizontalCenter
                                            }

                                            Text {
                                                text: modelData.value
                                                font.pixelSize: 20
                                                font.weight: Font.Bold
                                                color: modelData.color
                                                anchors.horizontalCenter: parent.horizontalCenter
                                            }

                                            Text {
                                                text: modelData.title
                                                font.pixelSize: 12
                                                color: "#64748b"
                                                anchors.horizontalCenter: parent.horizontalCenter
                                            }

                                            Text {
                                                text: modelData.subtitle
                                                font.pixelSize: 10
                                                color: "#94a3b8"
                                                anchors.horizontalCenter: parent.horizontalCenter
                                            }
                                        }
                                    }
                                }
                            }

                            // 筛选工具栏
                            Rectangle {
                                width: parent.width
                                height: 60
                                color: "#f8fafc"
                                radius: 8
                                border.width: 1
                                border.color: "#e2e8f0"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 12

                                    TextField {
                                        Layout.preferredWidth: 200
                                        placeholderText: "搜索学生姓名、学号..."
                                        height: 36
                                    }

                                    ComboBox {
                                        Layout.preferredWidth: 120
                                        model: ["全部班级", "高一(1)班", "高一(2)班", "高一(3)班"]
                                        height: 36
                                    }

                                    ComboBox {
                                        Layout.preferredWidth: 100
                                        model: ["全部性别", "男", "女"]
                                        height: 36
                                    }

                                    ComboBox {
                                        Layout.preferredWidth: 120
                                        model: ["全部状态", "在读", "休学", "转学", "毕业"]
                                        height: 36
                                    }

                                    Item {
                                        Layout.fillWidth: true
                                    }

                                    Button {
                                        text: "重置筛选"
                                        height: 36
                                    }
                                }
                            }

                            // 学生列表区域
                            Rectangle {
                                width: parent.width
                                height: parent.height - 220 // 减去统计卡片和筛选栏的高度
                                color: "#ffffff"
                                radius: 8
                                border.width: 1
                                border.color: "#e2e8f0"

                                ScrollView {
                                    anchors.fill: parent
                                    anchors.margins: 16

                                    GridLayout {
                                        width: parent.width
                                        columns: Math.floor(width / 280)
                                        columnSpacing: 16
                                        rowSpacing: 16

                                        Repeater {
                                            model: [
                                                {
                                                    name: "张三",
                                                    id: "2024001",
                                                    class: "高一(1)班",
                                                    gender: "男",
                                                    age: 16,
                                                    status: "在读",
                                                    avatar: "👦"
                                                },
                                                {
                                                    name: "李四",
                                                    id: "2024002",
                                                    class: "高一(1)班",
                                                    gender: "女",
                                                    age: 16,
                                                    status: "在读",
                                                    avatar: "👧"
                                                },
                                                {
                                                    name: "王五",
                                                    id: "2024003",
                                                    class: "高一(2)班",
                                                    gender: "男",
                                                    age: 17,
                                                    status: "在读",
                                                    avatar: "👦"
                                                },
                                                {
                                                    name: "赵六",
                                                    id: "2024004",
                                                    class: "高一(2)班",
                                                    gender: "女",
                                                    age: 16,
                                                    status: "休学",
                                                    avatar: "👧"
                                                },
                                                {
                                                    name: "钱七",
                                                    id: "2024005",
                                                    class: "高一(3)班",
                                                    gender: "男",
                                                    age: 17,
                                                    status: "在读",
                                                    avatar: "👦"
                                                },
                                                {
                                                    name: "孙八",
                                                    id: "2024006",
                                                    class: "高一(3)班",
                                                    gender: "女",
                                                    age: 16,
                                                    status: "在读",
                                                    avatar: "👧"
                                                }
                                            ]

                                            Rectangle {
                                                Layout.preferredWidth: 260
                                                Layout.preferredHeight: 140
                                                color: "#ffffff"
                                                radius: 8
                                                border.width: 1
                                                border.color: "#e2e8f0"

                                                MouseArea {
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    onEntered: {
                                                        parent.color = "#f8fafc";
                                                        parent.border.color = "#3b82f6";
                                                    }
                                                    onExited: {
                                                        parent.color = "#ffffff";
                                                        parent.border.color = "#e2e8f0";
                                                    }
                                                    onClicked: openDetailModal(modelData)
                                                }

                                                Column {
                                                    anchors.fill: parent
                                                    anchors.margins: 16
                                                    spacing: 8

                                                    Row {
                                                        width: parent.width
                                                        spacing: 12

                                                        Text {
                                                            text: modelData.avatar
                                                            font.pixelSize: 32
                                                        }

                                                        Column {
                                                            anchors.verticalCenter: parent.verticalCenter
                                                            spacing: 2

                                                            Text {
                                                                text: modelData.name
                                                                font.pixelSize: 16
                                                                font.weight: Font.DemiBold
                                                                color: "#1e293b"
                                                            }

                                                            Text {
                                                                text: "学号 " + modelData.id
                                                                font.pixelSize: 12
                                                                color: "#64748b"
                                                            }
                                                        }

                                                        Item {
                                                            Layout.fillWidth: true
                                                        }

                                                        Rectangle {
                                                            width: 50
                                                            height: 20
                                                            radius: 10
                                                            color: modelData.status === "在读" ? "#dcfce7" : modelData.status === "休学" ? "#fef3c7" : "#f3f4f6"

                                                            Text {
                                                                text: modelData.status
                                                                anchors.centerIn: parent
                                                                font.pixelSize: 10
                                                                color: modelData.status === "在读" ? "#166534" : modelData.status === "休学" ? "#92400e" : "#374151"
                                                            }
                                                        }
                                                    }

                                                    Rectangle {
                                                        width: parent.width
                                                        height: 1
                                                        color: "#e2e8f0"
                                                    }

                                                    Row {
                                                        width: parent.width
                                                        spacing: 16

                                                        Column {
                                                            Text {
                                                                text: "班级"
                                                                font.pixelSize: 10
                                                                color: "#94a3b8"
                                                            }
                                                            Text {
                                                                text: modelData.class
                                                                font.pixelSize: 12
                                                                color: "#64748b"
                                                            }
                                                        }

                                                        Column {
                                                            Text {
                                                                text: "性别"
                                                                font.pixelSize: 10
                                                                color: "#94a3b8"
                                                            }
                                                            Text {
                                                                text: modelData.gender
                                                                font.pixelSize: 12
                                                                color: "#64748b"
                                                            }
                                                        }

                                                        Column {
                                                            Text {
                                                                text: "年龄"
                                                                font.pixelSize: 10
                                                                color: "#94a3b8"
                                                            }
                                                            Text {
                                                                text: modelData.age + "岁"
                                                                font.pixelSize: 12
                                                                color: "#64748b"
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

                    // 右侧信息面板
                    Rectangle {
                        Layout.preferredWidth: 300
                        Layout.fillHeight: true
                        color: "#ffffff"
                        radius: 12
                        border.width: 1
                        border.color: "#e2e8f0"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 16

                            Text {
                                text: "快速操作"
                                font.pixelSize: 16
                                font.weight: Font.DemiBold
                                color: "#1e293b"
                            }

                            Column {
                                width: parent.width
                                spacing: 12

                                Repeater {
                                    model: [
                                        {
                                            title: "学生档案",
                                            desc: "查看和编辑学生详细信息",
                                            icon: "📋"
                                        },
                                        {
                                            title: "成绩录入",
                                            desc: "批量录入学生考试成绩",
                                            icon: "📝"
                                        },
                                        {
                                            title: "考勤管理",
                                            desc: "记录学生出勤情况",
                                            icon: "📅"
                                        },
                                        {
                                            title: "家长联系",
                                            desc: "管理家长联系方式",
                                            icon: "📞"
                                        }
                                    ]

                                    Rectangle {
                                        width: parent.width
                                        height: 60
                                        color: "#f8fafc"
                                        radius: 8
                                        border.width: 1
                                        border.color: "#e2e8f0"

                                        MouseArea {
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: {
                                                parent.color = "#f1f5f9";
                                                parent.border.color = "#3b82f6";
                                            }
                                            onExited: {
                                                parent.color = "#f8fafc";
                                                parent.border.color = "#e2e8f0";
                                            }
                                        }

                                        Row {
                                            anchors.fill: parent
                                            anchors.margins: 12
                                            spacing: 12

                                            Text {
                                                text: modelData.icon
                                                font.pixelSize: 20
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Column {
                                                anchors.verticalCenter: parent.verticalCenter
                                                spacing: 2

                                                Text {
                                                    text: modelData.title
                                                    font.pixelSize: 14
                                                    font.weight: Font.Medium
                                                    color: "#1e293b"
                                                }

                                                Text {
                                                    text: modelData.desc
                                                    font.pixelSize: 12
                                                    color: "#64748b"
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

            // 底部工具栏区域
            Rectangle {
                width: parent.width
                height: 60
                color: "#ffffff"
                radius: 12
                border.width: 1
                border.color: "#e2e8f0"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    Text {
                        id: statusText
                        text: "共 156 名学生 · 已选择 0 项"
                        font.pixelSize: 14
                        color: "#64748b"
                        Layout.fillWidth: true
                    }

                    Row {
                        spacing: 12

                        Button {
                            text: "批量操作"
                            enabled: false
                        }

                        Button {
                            text: "刷新数据"
                            onClicked: refreshView()
                        }
                    }
                }
            }
        }
    }

    // 详情模态框
    Dialog {
        id: detailModal
        title: "学生详情"
        width: 500
        height: 600
        anchors.centerIn: parent
        modal: true

        property var itemData: null

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: itemData ? "学生姓名：" + itemData.name : ""
                font.pixelSize: 16
            }

            Text {
                text: itemData ? "学号：" + itemData.id : ""
                font.pixelSize: 14
                color: "#64748b"
            }

            Text {
                text: itemData ? "班级：" + itemData.class : ""
                font.pixelSize: 14
                color: "#64748b"
            }

            Text {
                text: itemData ? "性别：" + itemData.gender : ""
                font.pixelSize: 14
                color: "#64748b"
            }

            Text {
                text: itemData ? "年龄：" + itemData.age + "岁" : ""
                font.pixelSize: 14
                color: "#64748b"
            }

            Text {
                text: itemData ? "状态：" + itemData.status : ""
                font.pixelSize: 14
                color: "#64748b"
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 添加学生对话框
    Dialog {
        id: addStudentDialog
        title: "添加学生"
        width: 400
        height: 500
        anchors.centerIn: parent
        modal: true

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
                model: ["高一(1)班", "高一(2)班", "高一(3)班"]
            }

            ComboBox {
                width: parent.width
                model: ["男", "女"]
            }

            TextField {
                width: parent.width
                placeholderText: "年龄"
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 批量导入对话框
    Dialog {
        id: importStudentsDialog
        title: "批量导入学生"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择要导入的文件（支持 Excel、CSV 格式）"
                font.pixelSize: 14
            }

            Rectangle {
                width: parent.width
                height: 200
                color: "#f8fafc"
                radius: 8
                border.width: 2
                border.color: "#e2e8f0"
                border.style: Qt.DashLine

                Column {
                    anchors.centerIn: parent
                    spacing: 12

                    Text {
                        text: "📁"
                        font.pixelSize: 48
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "拖拽文件到此处或点击选择文件"
                        color: "#64748b"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Button {
                        text: "选择文件"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            Text {
                text: "模板格式：姓名 | 学号 | 班级 | 性别 | 年龄 | 联系方式"
                color: "#64748b"
                font.pixelSize: 12
            }

            Button {
                text: "下载导入模板"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 导出数据对话框
    Dialog {
        id: exportStudentsDialog
        title: "导出学生数据"
        width: 400
        height: 300
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择导出格式和范围"
                font.pixelSize: 14
            }

            ComboBox {
                width: parent.width
                model: ["Excel 格式 (.xlsx)", "CSV 格式 (.csv)", "PDF 格式 (.pdf)"]
            }

            ComboBox {
                width: parent.width
                model: ["全部学生", "当前筛选结果", "已选择学生"]
            }

            CheckBox {
                text: "包含详细信息"
                checked: true
            }

            CheckBox {
                text: "包含联系方式"
                checked: false
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 刷新视图函数
    function refreshView() {
        console.log("刷新学生数据");
        statusText.text = "共 156 名学生 · 已选择 0 项 · 已刷新";
    }

    // 打开详情模态框函数
    function openDetailModal(data) {
        detailModal.itemData = data;
        statusText.text = "已选择：" + data.name + "（学号 " + data.id + "）";
        detailModal.open();
    }
}
