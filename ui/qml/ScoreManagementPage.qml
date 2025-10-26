import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"

FluentPage {
    id: scoreManagementPage
    title: "积分管理"

    // 页面状态
    property int currentView: 0 // 0: 成绩列表, 1: 统计分析, 2: 导入导出
    property var selectedCredit: null

    // 顶部分段控制器
    header: Rectangle {
        width: parent.width
        height: 60
        color: "#ffffff"
        border.color: "#e5e7eb"
        border.width: 1

        Row {
            anchors.centerIn: parent
            spacing: 2

            Repeater {
                model: ["积分列表", "统计分析", "导入导出"]

                Rectangle {
                    width: 120
                    height: 36
                    radius: 18
                    color: currentView === index ? "#0078d4" : "transparent"
                    border.color: currentView === index ? "#0078d4" : "#d1d5db"
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: modelData
                        color: currentView === index ? "#ffffff" : "#6b7280"
                        font.pixelSize: 14
                        font.weight: Font.Medium
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: currentView = index
                        cursorShape: Qt.PointingHandCursor
                    }
                }
            }
        }
    }

    // 主内容区域
    content: StackLayout {
        currentIndex: currentView

        // 成绩列表视图
        Item {
            RowLayout {
                anchors.fill: parent
                spacing: 16

                // 左侧筛选面板
                Rectangle {
                    Layout.preferredWidth: 280
                    Layout.fillHeight: true
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 20

                        Text {
                            text: "筛选条件"
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            color: "#111827"
                        }

                        // 班级筛选
                        Column {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "班级"
                                font.pixelSize: 14
                                color: "#374151"
                            }

                            ComboBox {
                                width: parent.width
                                model: ["全部班级", "高一(1)班", "高一(2)班", "高一(3)班"]
                                currentIndex: 0
                            }
                        }

                        // 科目筛选
                        Column {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "科目"
                                font.pixelSize: 14
                                color: "#374151"
                            }

                            ComboBox {
                                width: parent.width
                                model: ["全部科目", "语文", "数学", "英语", "物理", "化学"]
                                currentIndex: 0
                            }
                        }

                        // 考试类型筛选
                        Column {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "考试类型"
                                font.pixelSize: 14
                                color: "#374151"
                            }

                            ComboBox {
                                width: parent.width
                                model: ["全部类型", "平时成绩", "作业成绩", "考试成绩", "课堂表现"]
                                currentIndex: 0
                            }
                        }

                        // 分数范围
                        Column {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "分数范围"
                                font.pixelSize: 14
                                color: "#374151"
                            }

                            Row {
                                spacing: 8

                                SpinBox {
                                    width: 80
                                    from: 0
                                    to: 100
                                    value: 0
                                }

                                Text {
                                    text: "至"
                                    anchors.verticalCenter: parent.verticalCenter
                                    color: "#6b7280"
                                }

                                SpinBox {
                                    width: 80
                                    from: 0
                                    to: 100
                                    value: 100
                                }
                            }
                        }

                        // 搜索框
                        Column {
                            width: parent.width
                            spacing: 8

                            Text {
                                text: "搜索学生"
                                font.pixelSize: 14
                                color: "#374151"
                            }

                            TextField {
                                width: parent.width
                                placeholderText: "输入学生姓名..."
                            }
                        }

                        // 重置按钮
                        Button {
                            width: parent.width
                            text: "重置筛选"
                            flat: true
                        }
                    }
                }

                // 中间成绩列表
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        // 工具栏
                        Row {
                            width: parent.width
                            spacing: 12

                            Text {
                                text: "积分记录"
                                font.pixelSize: 18
                                font.weight: Font.Bold
                                color: "#111827"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                text: "添加积分"
                                highlighted: true
                                onClicked: addCreditDialog.open()
                            }

                            Button {
                                text: "批量导入"
                                onClicked: importScoresDialog.open()
                            }

                            Button {
                                text: "导出数据"
                                onClicked: exportScoresDialog.open()
                            }
                        }

                        // 成绩表格
                        Rectangle {
                            width: parent.width
                            height: parent.height - 60
                            color: "#f8fafc"
                            radius: 8
                            border.color: "#e5e7eb"
                            border.width: 1

                            Column {
                                anchors.fill: parent

                                // 表头
                                Rectangle {
                                    width: parent.width
                                    height: 50
                                    color: "#ffffff"
                                    radius: 8

                                    Row {
                                        anchors.fill: parent
                                        anchors.margins: 16
                                        spacing: 16

                                        Text {
                                            text: "学生"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 100
                                        }

                                        Text {
                                            text: "班级"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 100
                                        }

                                        Text {
                                            text: "科目"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 80
                                        }

                                        Text {
                                            text: "类型"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 100
                                        }

                                        Text {
                                            text: "分数"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 80
                                        }

                                        Text {
                                            text: "等级"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 60
                                        }

                                        Text {
                                            text: "日期"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 100
                                        }

                                        Text {
                                            text: "操作"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#374151"
                                            width: 120
                                        }
                                    }
                                }

                                // 成绩列表
                                ListView {
                                    width: parent.width
                                    height: parent.height - 50
                                    model: controller ? controller.credits : []
                                    spacing: 1

                                    delegate: Rectangle {
                                        width: parent.width
                                        height: 60
                                        color: index % 2 === 0 ? "#ffffff" : "#f8fafc"

                                        MouseArea {
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: parent.color = "#e0f2fe"
                                            onExited: parent.color = index % 2 === 0 ? "#ffffff" : "#f8fafc"
                                            onClicked: {
                                                selectedCredit = modelData
                                                creditDetailModal.open()
                                            }
                                        }

                                        Row {
                                            anchors.fill: parent
                                            anchors.margins: 16
                                            spacing: 16

                                            Text {
                                                text: modelData.studentName || "张三"
                                                font.pixelSize: 14
                                                color: "#111827"
                                                width: 100
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Text {
                                                text: modelData.className || "高一(1)班"
                                                font.pixelSize: 14
                                                color: "#6b7280"
                                                width: 100
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Text {
                                                text: modelData.subcategory || "项目"
                                                font.pixelSize: 14
                                                color: "#6b7280"
                                                width: 80
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Text {
                                                text: modelData.category || "积分类别"
                                                font.pixelSize: 14
                                                color: "#6b7280"
                                                width: 100
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Text {
                                                text: (modelData.score || 85).toString()
                                                font.pixelSize: 16
                                                font.weight: Font.Bold
                                                color: (modelData.score || 85) >= 90 ? "#10b981" :
                                                       (modelData.score || 85) >= 80 ? "#3b82f6" :
                                                       (modelData.score || 85) >= 60 ? "#f59e0b" : "#ef4444"
                                                width: 80
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Rectangle {
                                                width: 40
                                                height: 24
                                                radius: 12
                                                color: (modelData.score || 85) >= 90 ? "#dcfce7" :
                                                       (modelData.score || 85) >= 80 ? "#dbeafe" :
                                                       (modelData.score || 85) >= 60 ? "#fef3c7" : "#fee2e2"
                                                anchors.verticalCenter: parent.verticalCenter

                                                Text {
                                                    text: (modelData.score || 85) >= 90 ? "优" :
                                                          (modelData.score || 85) >= 80 ? "良" :
                                                          (modelData.score || 85) >= 60 ? "及格" : "不及格"
                                                    anchors.centerIn: parent
                                                    font.pixelSize: 12
                                                    font.weight: Font.Bold
                                                    color: (modelData.score || 85) >= 90 ? "#166534" :
                                                           (modelData.score || 85) >= 80 ? "#1e40af" :
                                                           (modelData.score || 85) >= 60 ? "#92400e" : "#dc2626"
                                                }
                                            }

                                            Text {
                                                text: "2024-01-15"
                                                font.pixelSize: 14
                                                color: "#6b7280"
                                                width: 100
                                                anchors.verticalCenter: parent.verticalCenter
                                            }

                                            Row {
                                                spacing: 8
                                                anchors.verticalCenter: parent.verticalCenter

                                                Button {
                                                    text: "编辑"
                                                    flat: true
                                                    font.pixelSize: 12
                                                    onClicked: {
                                                        selectedCredit = modelData
                                                        editCreditDialog.open()
                                                    }
                                                }

                                                Button {
                                                    text: "删除"
                                                    flat: true
                                                    font.pixelSize: 12
                                                    palette.buttonText: "#dc2626"
                                                    onClicked: {
                                                        selectedCredit = modelData
                                                        deleteCreditDialog.open()
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
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 20

                        Text {
                            text: "成绩统计"
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            color: "#111827"
                        }

                        // 统计卡片
                        Column {
                            width: parent.width
                            spacing: 12

                            StatCard {
                                width: parent.width
                                title: "总记录数"
                                value: "1,234"
                                subtitle: "成绩记录"
                                iconText: "📊"
                                color: "#3b82f6"
                            }

                            StatCard {
                                width: parent.width
                                title: "平均分"
                                value: "82.5"
                                subtitle: "全科平均"
                                iconText: "📈"
                                color: "#10b981"
                            }

                            StatCard {
                                width: parent.width
                                title: "优秀率"
                                value: "68%"
                                subtitle: "90分以上"
                                iconText: "🏆"
                                color: "#f59e0b"
                            }

                            StatCard {
                                width: parent.width
                                title: "及格率"
                                value: "92%"
                                subtitle: "60分以上"
                                iconText: "✅"
                                color: "#8b5cf6"
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: 1
                            color: "#e5e7eb"
                        }

                        Text {
                            text: "快速操作"
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            color: "#111827"
                        }

                        Column {
                            width: parent.width
                            spacing: 8

                            Button {
                                width: parent.width
                                text: "📝 录入积分"
                                onClicked: addCreditDialog.open()
                            }

                            Button {
                                width: parent.width
                                text: "📊 生成报表"
                                onClicked: generateReportDialog.open()
                            }

                            Button {
                                width: parent.width
                                text: "📤 导出Excel"
                                onClicked: exportScoresDialog.open()
                            }

                            Button {
                                width: parent.width
                                text: "🔄 刷新数据"
                                onClicked: refreshCredits()
                            }
                        }
                    }
                }
            }
        }

        // 统计分析视图
        Item {
            Rectangle {
                anchors.fill: parent
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"
                border.width: 1

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    Text {
                        text: "📊"
                        font.pixelSize: 64
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "统计分析功能"
                        font.pixelSize: 18
                        font.weight: Font.Bold
                        color: "#111827"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "成绩趋势图表、班级对比分析等功能正在开发中..."
                        color: "#6b7280"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        // 导入导出视图
        Item {
            Rectangle {
                anchors.fill: parent
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"
                border.width: 1

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    Text {
                        text: "📁"
                        font.pixelSize: 64
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "数据导入导出"
                        font.pixelSize: 18
                        font.weight: Font.Bold
                        color: "#111827"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "批量导入Excel文件、导出成绩报表等功能正在开发中..."
                        color: "#6b7280"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }
    }

    // 积分详情模态框
    Dialog {
        id: creditDetailModal
        title: "积分详情"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "学生信息"
                font.pixelSize: 16
                font.weight: Font.Bold
                color: "#111827"
            }

            Rectangle {
                width: parent.width
                height: 200
                color: "#f8fafc"
                radius: 8
                border.color: "#e5e7eb"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Row {
                        spacing: 16
                        Text { text: "姓名:"; width: 80; color: "#374151" }
                        Text { text: selectedCredit ? selectedCredit.studentName || "张三" : "张三"; color: "#111827" }
                    }

                    Row {
                        spacing: 16
                        Text { text: "班级:"; width: 80; color: "#374151" }
                        Text { text: selectedCredit ? selectedCredit.className || "高一(1)班" : "高一(1)班"; color: "#111827" }
                    }

                    Row {
                        spacing: 16
                        Text { text: "科目:"; width: 80; color: "#374151" }
                        Text { text: selectedCredit ? selectedCredit.subcategory || "项目" : "项目"; color: "#111827" }
                    }

                    Row {
                        spacing: 16
                        Text { text: "类型:"; width: 80; color: "#374151" }
                        Text { text: selectedCredit ? selectedCredit.category || "积分类别" : "积分类别"; color: "#111827" }
                    }

                    Row {
                        spacing: 16
                        Text { text: "分数:"; width: 80; color: "#374151" }
                        Text {
                            text: selectedCredit ? (selectedCredit.score || 85).toString() : "85"
                            color: "#111827"
                            font.weight: Font.Bold
                        }
                    }

                    Row {
                        spacing: 16
                        Text { text: "日期:"; width: 80; color: "#374151" }
                        Text { text: "2024-01-15"; color: "#111827" }
                    }
                }
            }
        }

        standardButtons: Dialog.Close
    }

    // 添加积分对话框
    Dialog {
        id: addCreditDialog
        title: "添加积分记录"
        width: 500
        height: 450
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Row {
                spacing: 16
                Text { text: "学生:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["张三", "李四", "王五", "赵六", "钱七"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "班级:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["高一(1)班", "高一(2)班", "高一(3)班"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "科目:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["语文", "数学", "英语", "物理", "化学", "生物"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "类型:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["平时成绩", "作业成绩", "考试成绩", "课堂表现"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "分数:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                SpinBox {
                    from: 0
                    to: 100
                    value: 85
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "备注:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                TextField {
                    placeholderText: "可选备注信息"
                    width: 200
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 编辑积分对话框
    Dialog {
        id: editCreditDialog
        title: "编辑积分记录"
        width: 500
        height: 450
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Row {
                spacing: 16
                Text { text: "学生:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["张三", "李四", "王五", "赵六", "钱七"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "班级:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["高一(1)班", "高一(2)班", "高一(3)班"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "科目:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["语文", "数学", "英语", "物理", "化学", "生物"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "类型:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["平时成绩", "作业成绩", "考试成绩", "课堂表现"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "分数:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                SpinBox {
                    from: 0
                    to: 100
                    value: selectedCredit ? selectedCredit.score || 85 : 85
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "备注:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                TextField {
                    placeholderText: "可选备注信息"
                    text: selectedCredit ? selectedCredit.note || "" : ""
                    width: 200
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 删除积分确认对话框
    Dialog {
        id: deleteCreditDialog
        title: "确认删除"
        width: 400
        height: 200
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.centerIn: parent
            spacing: 16

            Text {
                text: "确定要删除这条成绩记录吗？"
                font.pixelSize: 16
                color: "#111827"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "此操作不可撤销"
                font.pixelSize: 14
                color: "#6b7280"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 批量导入对话框
    Dialog {
        id: importScoresDialog
        title: "批量导入成绩"
        width: 600
        height: 500
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "支持导入 Excel (.xlsx) 和 CSV (.csv) 格式文件"
                color: "#6b7280"
            }

            Rectangle {
                width: parent.width
                height: 200
                color: "#f9fafb"
                border.color: "#d1d5db"
                border.width: 2
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

            Text {
                text: "模板格式：学号 | 姓名 | 科目 | 成绩类型 | 分数 | 备注"
                color: "#6b7280"
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
        id: exportScoresDialog
        title: "导出成绩数据"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择导出格式和范围"
                font.pixelSize: 16
                font.weight: Font.Bold
                color: "#111827"
            }

            Row {
                spacing: 16
                Text { text: "格式:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["Excel (.xlsx)", "CSV (.csv)", "PDF报表"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "范围:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["全部数据", "当前筛选结果", "选中记录"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "班级:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["全部班级", "高一(1)班", "高一(2)班", "高一(3)班"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "科目:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["全部科目", "语文", "数学", "英语", "物理", "化学"]
                    width: 200
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 生成报表对话框
    Dialog {
        id: generateReportDialog
        title: "生成成绩报表"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择报表类型和参数"
                font.pixelSize: 16
                font.weight: Font.Bold
                color: "#111827"
            }

            Row {
                spacing: 16
                Text { text: "类型:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["班级成绩单", "学生个人报告", "科目统计报告", "成绩趋势分析"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "班级:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["全部班级", "高一(1)班", "高一(2)班", "高一(3)班"]
                    width: 200
                }
            }

            Row {
                spacing: 16
                Text { text: "时间:"; width: 80; anchors.verticalCenter: parent.verticalCenter }
                ComboBox {
                    model: ["本学期", "本月", "最近一周", "自定义"]
                    width: 200
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 刷新数据函数
    function refreshCredits() {
        if (controller) {
            controller.refreshCredits()
        }
    }
}
