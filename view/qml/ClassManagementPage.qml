import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: classManagementPage

    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24

        // 页面标题和操作栏
        Row {
            width: parent.width
            spacing: 16

            Column {
                Text {
                    text: "班级管理"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "管理班级信息，查看班级统计和学生分布"
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
                    text: "新建班级"
                    highlighted: true
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 5v14m-7-7h14'/%3E%3C/svg%3E"
                    onClicked: addClassDialog.open()
                }

                Button {
                    text: "班级设置"
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E"
                    onClicked: classSettingsDialog.open()
                }

                Button {
                    text: "导出报告"
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpolyline points='7,10 12,15 17,10'/%3E%3Cline x1='12' y1='15' x2='12' y2='3'/%3E%3C/svg%3E"
                    onClicked: exportReportDialog.open()
                }
            }
        }

        // 快速统计卡片
        Row {
            width: parent.width
            spacing: 16

            StatCard {
                title: "班级总数"
                value: "12"
                subtitle: "本学期新增 2 个班级"
                icon: "🏫"
                color: "#3b82f6"
                width: (parent.width - 48) / 4
            }

            StatCard {
                title: "学生总数"
                value: "456"
                subtitle: "平均每班 38 人"
                icon: "👥"
                color: "#10b981"
                width: (parent.width - 48) / 4
            }

            StatCard {
                title: "班主任数"
                value: "12"
                subtitle: "配备率 100%"
                icon: "👨‍🏫"
                color: "#f59e0b"
                width: (parent.width - 48) / 4
            }

            StatCard {
                title: "平均成绩"
                value: "85.6"
                subtitle: "较上月提升 2.3 分"
                icon: "📊"
                color: "#8b5cf6"
                width: (parent.width - 48) / 4
            }
        }

        // 年级筛选和搜索
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

                // 年级筛选
                ComboBox {
                    width: 120
                    height: 40
                    model: ["全部年级", "高一年级", "高二年级", "高三年级"]
                    anchors.verticalCenter: parent.verticalCenter
                }

                // 搜索框
                TextField {
                    width: 300
                    height: 40
                    placeholderText: "搜索班级名称或班主任..."
                    anchors.verticalCenter: parent.verticalCenter

                    background: Rectangle {
                        color: "#f9fafb"
                        radius: 8
                        border.color: parent.activeFocus ? "#3b82f6" : "#d1d5db"
                    }
                }

                Item {
                    Layout.fillWidth: true
                }

                // 视图切换
                Row {
                    spacing: 4
                    anchors.verticalCenter: parent.verticalCenter

                    Button {
                        text: "卡片视图"
                        height: 40
                        checkable: true
                        checked: true
                        ButtonGroup.group: viewGroup
                    }

                    Button {
                        text: "列表视图"
                        height: 40
                        checkable: true
                        ButtonGroup.group: viewGroup
                    }

                    ButtonGroup {
                        id: viewGroup
                    }
                }
            }
        }

        // 班级卡片网格
        GridView {
            width: parent.width
            height: 600
            cellWidth: (width - 32) / 3
            cellHeight: 280
            model: [
                {
                    name: "高一(1)班",
                    teacher: "张老师",
                    studentCount: 42,
                    avgScore: 87.5,
                    classroom: "A101",
                    subjects: ["语文", "数学", "英语", "物理", "化学"],
                    status: "正常"
                },
                {
                    name: "高一(2)班",
                    teacher: "李老师",
                    studentCount: 40,
                    avgScore: 85.2,
                    classroom: "A102",
                    subjects: ["语文", "数学", "英语", "物理", "化学"],
                    status: "正常"
                },
                {
                    name: "高一(3)班",
                    teacher: "王老师",
                    studentCount: 38,
                    avgScore: 86.8,
                    classroom: "A103",
                    subjects: ["语文", "数学", "英语", "物理", "化学"],
                    status: "正常"
                },
                {
                    name: "高二(1)班",
                    teacher: "赵老师",
                    studentCount: 39,
                    avgScore: 82.3,
                    classroom: "B201",
                    subjects: ["语文", "数学", "英语", "物理", "化学", "生物"],
                    status: "正常"
                },
                {
                    name: "高二(2)班",
                    teacher: "钱老师",
                    studentCount: 41,
                    avgScore: 84.7,
                    classroom: "B202",
                    subjects: ["语文", "数学", "英语", "物理", "化学", "生物"],
                    status: "正常"
                },
                {
                    name: "高三(1)班",
                    teacher: "孙老师",
                    studentCount: 35,
                    avgScore: 88.9,
                    classroom: "C301",
                    subjects: ["语文", "数学", "英语", "物理", "化学", "生物"],
                    status: "毕业班"
                }
            ]

            delegate: Rectangle {
                width: GridView.view.cellWidth - 16
                height: GridView.view.cellHeight - 16
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.border.color = "#3b82f6"
                    onExited: parent.border.color = "#e5e7eb"
                    onClicked: {
                        classDetailDialog.classData = modelData;
                        classDetailDialog.open();
                    }
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 12

                    // 班级头部信息
                    Row {
                        width: parent.width
                        spacing: 12

                        Rectangle {
                            width: 50
                            height: 50
                            radius: 25
                            color: "#f3f4f6"

                            Text {
                                text: modelData.name.charAt(2)
                                font.pixelSize: 20
                                font.weight: Font.Bold
                                color: "#6b7280"
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            spacing: 4
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: modelData.name
                                font.pixelSize: 18
                                font.weight: Font.Bold
                                color: "#111827"
                            }

                            Text {
                                text: "班主任: " + modelData.teacher
                                font.pixelSize: 12
                                color: "#6b7280"
                            }

                            Rectangle {
                                width: 60
                                height: 20
                                radius: 10
                                color: modelData.status === "正常" ? "#dcfce7" : "#fef3c7"

                                Text {
                                    text: modelData.status
                                    anchors.centerIn: parent
                                    font.pixelSize: 10
                                    color: modelData.status === "正常" ? "#166534" : "#92400e"
                                }
                            }
                        }
                    }

                    // 统计信息
                    Rectangle {
                        width: parent.width
                        height: 80
                        color: "#f9fafb"
                        radius: 8

                        Row {
                            anchors.fill: parent
                            anchors.margins: 12

                            Column {
                                width: parent.width / 3
                                spacing: 4

                                Text {
                                    text: modelData.studentCount
                                    font.pixelSize: 20
                                    font.weight: Font.Bold
                                    color: "#3b82f6"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                Text {
                                    text: "学生人数"
                                    font.pixelSize: 10
                                    color: "#6b7280"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }

                            Column {
                                width: parent.width / 3
                                spacing: 4

                                Text {
                                    text: modelData.avgScore
                                    font.pixelSize: 20
                                    font.weight: Font.Bold
                                    color: "#10b981"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                Text {
                                    text: "平均成绩"
                                    font.pixelSize: 10
                                    color: "#6b7280"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }

                            Column {
                                width: parent.width / 3
                                spacing: 4

                                Text {
                                    text: modelData.subjects.length
                                    font.pixelSize: 20
                                    font.weight: Font.Bold
                                    color: "#f59e0b"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                Text {
                                    text: "开设科目"
                                    font.pixelSize: 10
                                    color: "#6b7280"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                    }

                    // 教室信息
                    Row {
                        width: parent.width
                        spacing: 8

                        Text {
                            text: "📍"
                            font.pixelSize: 14
                        }

                        Text {
                            text: "教室: " + modelData.classroom
                            font.pixelSize: 12
                            color: "#6b7280"
                        }
                    }

                    // 操作按钮
                    Row {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "查看详情"
                            height: 32
                            width: (parent.width - 8) / 2
                            font.pixelSize: 12
                            onClicked: {
                                classDetailDialog.classData = modelData;
                                classDetailDialog.open();
                            }
                        }

                        Button {
                            text: "编辑班级"
                            height: 32
                            width: (parent.width - 8) / 2
                            font.pixelSize: 12
                            onClicked: {
                                editClassDialog.classData = modelData;
                                editClassDialog.open();
                            }
                        }
                    }
                }
            }
        }
    }

    // 新建班级对话框
    Dialog {
        id: addClassDialog
        title: "新建班级"
        width: 500
        height: 500
        anchors.centerIn: parent
        modal: true

        ScrollView {
            anchors.fill: parent

            Column {
                width: parent.width
                spacing: 16

                // 基本信息
                Text {
                    text: "基本信息"
                    font.weight: Font.Medium
                    color: "#374151"
                }

                Row {
                    width: parent.width
                    spacing: 16

                    Column {
                        width: (parent.width - 16) / 2
                        spacing: 8

                        Text {
                            text: "班级名称 *"
                            font.pixelSize: 12
                            color: "#374151"
                        }

                        TextField {
                            width: parent.width
                            placeholderText: "如：高一(4)班"
                        }
                    }

                    Column {
                        width: (parent.width - 16) / 2
                        spacing: 8

                        Text {
                            text: "年级 *"
                            font.pixelSize: 12
                            color: "#374151"
                        }

                        ComboBox {
                            width: parent.width
                            model: ["高一年级", "高二年级", "高三年级"]
                        }
                    }
                }

                Row {
                    width: parent.width
                    spacing: 16

                    Column {
                        width: (parent.width - 16) / 2
                        spacing: 8

                        Text {
                            text: "班主任 *"
                            font.pixelSize: 12
                            color: "#374151"
                        }

                        ComboBox {
                            width: parent.width
                            model: ["张老师", "李老师", "王老师", "赵老师", "钱老师"]
                            editable: true
                        }
                    }

                    Column {
                        width: (parent.width - 16) / 2
                        spacing: 8

                        Text {
                            text: "教室"
                            font.pixelSize: 12
                            color: "#374151"
                        }

                        TextField {
                            width: parent.width
                            placeholderText: "如：A104"
                        }
                    }
                }

                Row {
                    width: parent.width
                    spacing: 16

                    Column {
                        width: (parent.width - 16) / 2
                        spacing: 8

                        Text {
                            text: "计划人数"
                            font.pixelSize: 12
                            color: "#374151"
                        }

                        SpinBox {
                            width: parent.width
                            from: 20
                            to: 50
                            value: 40
                        }
                    }

                    Column {
                        width: (parent.width - 16) / 2
                        spacing: 8

                        Text {
                            text: "开班时间"
                            font.pixelSize: 12
                            color: "#374151"
                        }

                        TextField {
                            width: parent.width
                            placeholderText: "YYYY-MM-DD"
                        }
                    }
                }

                // 科目设置
                Text {
                    text: "科目设置"
                    font.weight: Font.Medium
                    color: "#374151"
                }

                Flow {
                    width: parent.width
                    spacing: 8

                    Repeater {
                        model: ["语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理"]

                        CheckBox {
                            text: modelData
                            checked: ["语文", "数学", "英语", "物理", "化学"].includes(modelData)
                        }
                    }
                }

                Column {
                    width: parent.width
                    spacing: 8

                    Text {
                        text: "班级描述"
                        font.pixelSize: 12
                        color: "#374151"
                    }

                    ScrollView {
                        width: parent.width
                        height: 80

                        TextArea {
                            placeholderText: "班级特色、教学目标等..."
                            wrapMode: TextArea.Wrap
                        }
                    }
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 班级详情对话框
    Dialog {
        id: classDetailDialog
        title: "班级详情"
        width: 600
        height: 700
        anchors.centerIn: parent
        modal: true

        property var classData: ({})

        ScrollView {
            anchors.fill: parent

            Column {
                width: parent.width
                spacing: 20

                // 班级头部信息
                Rectangle {
                    width: parent.width
                    height: 120
                    color: "#f8fafc"
                    radius: 12

                    Row {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 20

                        Rectangle {
                            width: 80
                            height: 80
                            radius: 40
                            color: "#3b82f6"

                            Text {
                                text: classDetailDialog.classData.name ? classDetailDialog.classData.name.charAt(2) : ""
                                font.pixelSize: 32
                                font.weight: Font.Bold
                                color: "white"
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            spacing: 8
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: classDetailDialog.classData.name || ""
                                font.pixelSize: 24
                                font.weight: Font.Bold
                                color: "#111827"
                            }

                            Text {
                                text: "班主任: " + (classDetailDialog.classData.teacher || "")
                                font.pixelSize: 14
                                color: "#6b7280"
                            }

                            Text {
                                text: "教室: " + (classDetailDialog.classData.classroom || "")
                                font.pixelSize: 14
                                color: "#6b7280"
                            }

                            Rectangle {
                                width: 80
                                height: 24
                                radius: 12
                                color: "#dcfce7"

                                Text {
                                    text: classDetailDialog.classData.status || ""
                                    anchors.centerIn: parent
                                    font.pixelSize: 12
                                    color: "#166534"
                                }
                            }
                        }
                    }
                }

                // 统计信息
                Row {
                    width: parent.width
                    spacing: 16

                    Rectangle {
                        width: (parent.width - 32) / 3
                        height: 100
                        color: "#ffffff"
                        radius: 8
                        border.color: "#e5e7eb"

                        Column {
                            anchors.centerIn: parent
                            spacing: 8

                            Text {
                                text: classDetailDialog.classData.studentCount || "0"
                                font.pixelSize: 28
                                font.weight: Font.Bold
                                color: "#3b82f6"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: "学生人数"
                                font.pixelSize: 12
                                color: "#6b7280"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    Rectangle {
                        width: (parent.width - 32) / 3
                        height: 100
                        color: "#ffffff"
                        radius: 8
                        border.color: "#e5e7eb"

                        Column {
                            anchors.centerIn: parent
                            spacing: 8

                            Text {
                                text: classDetailDialog.classData.avgScore || "0"
                                font.pixelSize: 28
                                font.weight: Font.Bold
                                color: "#10b981"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: "平均成绩"
                                font.pixelSize: 12
                                color: "#6b7280"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    Rectangle {
                        width: (parent.width - 32) / 3
                        height: 100
                        color: "#ffffff"
                        radius: 8
                        border.color: "#e5e7eb"

                        Column {
                            anchors.centerIn: parent
                            spacing: 8

                            Text {
                                text: classDetailDialog.classData.subjects ? classDetailDialog.classData.subjects.length : "0"
                                font.pixelSize: 28
                                font.weight: Font.Bold
                                color: "#f59e0b"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: "开设科目"
                                font.pixelSize: 12
                                color: "#6b7280"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }
                }

                // 开设科目
                Column {
                    width: parent.width
                    spacing: 12

                    Text {
                        text: "开设科目"
                        font.pixelSize: 16
                        font.weight: Font.Medium
                        color: "#111827"
                    }

                    Flow {
                        width: parent.width
                        spacing: 8

                        Repeater {
                            model: classDetailDialog.classData.subjects || []

                            Rectangle {
                                width: subjectText.width + 16
                                height: 32
                                color: "#f0f9ff"
                                radius: 16
                                border.color: "#3b82f6"

                                Text {
                                    id: subjectText
                                    text: modelData
                                    anchors.centerIn: parent
                                    font.pixelSize: 12
                                    color: "#1d4ed8"
                                }
                            }
                        }
                    }
                }

                // 操作按钮
                Row {
                    width: parent.width
                    spacing: 12

                    Button {
                        text: "查看学生"
                        width: (parent.width - 24) / 3
                        highlighted: true
                    }

                    Button {
                        text: "成绩统计"
                        width: (parent.width - 24) / 3
                    }

                    Button {
                        text: "编辑班级"
                        width: (parent.width - 24) / 3
                    }
                }
            }
        }

        standardButtons: Dialog.Close
    }

    // 编辑班级对话框
    Dialog {
        id: editClassDialog
        title: "编辑班级"
        width: 500
        height: 500
        anchors.centerIn: parent
        modal: true

        property var classData: ({})

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 简化其他对话框定义...
    Dialog {
        id: classSettingsDialog
        title: "班级设置"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }
    Dialog {
        id: exportReportDialog
        title: "导出班级报告"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }
}
