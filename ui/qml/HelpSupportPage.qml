import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: helpSupportPage

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
                    text: "帮助与支持"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "获取使用帮助，解决常见问题，联系技术支持"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }

            Item { Layout.fillWidth: true }

            Row {
                spacing: 12
                anchors.verticalCenter: parent.verticalCenter

                Button {
                    text: "用户手册"
                    highlighted: true
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M4 19.5A2.5 2.5 0 0 1 6.5 17H20'/%3E%3Cpath d='M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'/%3E%3C/svg%3E"
                }

                Button {
                    text: "视频教程"
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpolygon points='5,3 19,12 5,21'/%3E%3C/svg%3E"
                }

                Button {
                    text: "联系支持"
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M22 12h-4l-3 9L9 3l-3 9H2'/%3E%3C/svg%3E"
                    onClicked: contactSupportDialog.open()
                }
            }
        }

        // 快速帮助卡片
        Row {
            width: parent.width
            spacing: 16

            // 快速入门
            Rectangle {
                width: (parent.width - 48) / 4
                height: 160
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.color = "#f9fafb"
                    onExited: parent.color = "#ffffff"
                    onClicked: quickStartDialog.open()
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Rectangle {
                        width: 48
                        height: 48
                        radius: 12
                        color: "#dcfce7"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Text {
                            text: "🚀"
                            font.pixelSize: 24
                            anchors.centerIn: parent
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 4

                        Text {
                            text: "快速入门"
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            color: "#111827"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: "5分钟上手指南"
                            font.pixelSize: 12
                            color: "#6b7280"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            // 常见问题
            Rectangle {
                width: (parent.width - 48) / 4
                height: 160
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.color = "#f9fafb"
                    onExited: parent.color = "#ffffff"
                    onClicked: faqDialog.open()
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Rectangle {
                        width: 48
                        height: 48
                        radius: 12
                        color: "#dbeafe"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Text {
                            text: "❓"
                            font.pixelSize: 24
                            anchors.centerIn: parent
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 4

                        Text {
                            text: "常见问题"
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            color: "#111827"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: "FAQ解答"
                            font.pixelSize: 12
                            color: "#6b7280"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            // 功能介绍
            Rectangle {
                width: (parent.width - 48) / 4
                height: 160
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.color = "#f9fafb"
                    onExited: parent.color = "#ffffff"
                    onClicked: featuresDialog.open()
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Rectangle {
                        width: 48
                        height: 48
                        radius: 12
                        color: "#fef3c7"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Text {
                            text: "⭐"
                            font.pixelSize: 24
                            anchors.centerIn: parent
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 4

                        Text {
                            text: "功能介绍"
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            color: "#111827"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: "详细功能说明"
                            font.pixelSize: 12
                            color: "#6b7280"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            // 更新日志
            Rectangle {
                width: (parent.width - 48) / 4
                height: 160
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.color = "#f9fafb"
                    onExited: parent.color = "#ffffff"
                    onClicked: changelogDialog.open()
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Rectangle {
                        width: 48
                        height: 48
                        radius: 12
                        color: "#f3e8ff"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Text {
                            text: "📝"
                            font.pixelSize: 24
                            anchors.centerIn: parent
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 4

                        Text {
                            text: "更新日志"
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            color: "#111827"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: "版本更新记录"
                            font.pixelSize: 12
                            color: "#6b7280"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }
        }

        // 系统信息
        Rectangle {
            width: parent.width
            height: 200
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16

                Text {
                    text: "系统信息"
                    font.pixelSize: 18
                    font.weight: Font.Medium
                    color: "#111827"
                }

                Row {
                    width: parent.width
                    spacing: 32

                    Column {
                        spacing: 12

                        Row {
                            spacing: 16
                            Text {
                                text: "软件版本:"
                                font.weight: Font.Medium
                                color: "#374151"
                                width: 80
                            }
                            Text {
                                text: "v2.1.0"
                                color: "#6b7280"
                            }
                        }

                        Row {
                            spacing: 16
                            Text {
                                text: "构建日期:"
                                font.weight: Font.Medium
                                color: "#374151"
                                width: 80
                            }
                            Text {
                                text: "2024-01-15"
                                color: "#6b7280"
                            }
                        }

                        Row {
                            spacing: 16
                            Text {
                                text: "运行环境:"
                                font.weight: Font.Medium
                                color: "#374151"
                                width: 80
                            }
                            Text {
                                text: "Qt 6.5.0"
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        spacing: 12

                        Row {
                            spacing: 16
                            Text {
                                text: "操作系统:"
                                font.weight: Font.Medium
                                color: "#374151"
                                width: 80
                            }
                            Text {
                                text: "Windows 11"
                                color: "#6b7280"
                            }
                        }

                        Row {
                            spacing: 16
                            Text {
                                text: "数据库:"
                                font.weight: Font.Medium
                                color: "#374151"
                                width: 80
                            }
                            Text {
                                text: "SQLite 3.42.0"
                                color: "#6b7280"
                            }
                        }

                        Row {
                            spacing: 16
                            Text {
                                text: "许可证:"
                                font.weight: Font.Medium
                                color: "#374151"
                                width: 80
                            }
                            Text {
                                text: "MIT License"
                                color: "#6b7280"
                            }
                        }
                    }
                }

                Row {
                    spacing: 12

                    Button {
                        text: "检查更新"
                        onClicked: checkUpdateDialog.open()
                    }

                    Button {
                        text: "系统诊断"
                        onClicked: systemDiagnosisDialog.open()
                    }

                    Button {
                        text: "导出日志"
                        onClicked: exportLogsDialog.open()
                    }
                }
            }
        }

        // 联系方式和支持
        Row {
            width: parent.width
            spacing: 16

            // 技术支持
            Rectangle {
                width: (parent.width - 16) / 2
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
                                text: "🛠️"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "技术支持"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "遇到问题？我们来帮您解决"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Row {
                            spacing: 8
                            Text {
                                text: "📧 邮箱:"
                                font.pixelSize: 12
                                color: "#374151"
                            }
                            Text {
                                text: "support@classmanager.com"
                                font.pixelSize: 12
                                color: "#3b82f6"
                            }
                        }

                        Row {
                            spacing: 8
                            Text {
                                text: "📞 电话:"
                                font.pixelSize: 12
                                color: "#374151"
                            }
                            Text {
                                text: "400-123-4567"
                                font.pixelSize: 12
                                color: "#3b82f6"
                            }
                        }

                        Row {
                            spacing: 8
                            Text {
                                text: "💬 QQ群:"
                                font.pixelSize: 12
                                color: "#374151"
                            }
                            Text {
                                text: "123456789"
                                font.pixelSize: 12
                                color: "#3b82f6"
                            }
                        }

                        Row {
                            spacing: 8
                            Text {
                                text: "🕒 工作时间:"
                                font.pixelSize: 12
                                color: "#374151"
                            }
                            Text {
                                text: "周一至周五 9:00-18:00"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }
                }
            }

            // 反馈建议
            Rectangle {
                width: (parent.width - 16) / 2
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
                                text: "💡"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "反馈建议"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "您的建议让我们更好"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 12

                        Button {
                            text: "功能建议"
                            width: parent.width
                            onClicked: featureSuggestionDialog.open()
                        }

                        Button {
                            text: "问题反馈"
                            width: parent.width
                            onClicked: bugReportDialog.open()
                        }

                        Button {
                            text: "用户体验调研"
                            width: parent.width
                            onClicked: surveyDialog.open()
                        }
                    }
                }
            }
        }
    }

    // 快速入门对话框
    Dialog {
        id: quickStartDialog
        title: "快速入门指南"
        width: 600
        height: 500
        anchors.centerIn: parent
        modal: true

        ScrollView {
            anchors.fill: parent

            Column {
                width: parent.width
                spacing: 16

                Text {
                    text: "欢迎使用班级管理系统！"
                    font.pixelSize: 18
                    font.weight: Font.Bold
                    color: "#111827"
                }

                Text {
                    text: "以下是快速上手的几个步骤："
                    font.pixelSize: 14
                    color: "#6b7280"
                    wrapMode: Text.WordWrap
                    width: parent.width
                }

                Column {
                    width: parent.width
                    spacing: 12

                    Rectangle {
                        width: parent.width
                        height: 60
                        color: "#f9fafb"
                        radius: 8

                        Row {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Rectangle {
                                width: 36
                                height: 36
                                radius: 18
                                color: "#3b82f6"
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "1"
                                    color: "white"
                                    font.weight: Font.Bold
                                    anchors.centerIn: parent
                                }
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                Text {
                                    text: "添加学生信息"
                                    font.weight: Font.Medium
                                    color: "#111827"
                                }
                                Text {
                                    text: "在学生管理页面添加班级学生的基本信息"
                                    font.pixelSize: 12
                                    color: "#6b7280"
                                }
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 60
                        color: "#f9fafb"
                        radius: 8

                        Row {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Rectangle {
                                width: 36
                                height: 36
                                radius: 18
                                color: "#10b981"
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "2"
                                    color: "white"
                                    font.weight: Font.Bold
                                    anchors.centerIn: parent
                                }
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                Text {
                                    text: "录入成绩数据"
                                    font.weight: Font.Medium
                                    color: "#111827"
                                }
                                Text {
                                    text: "在成绩管理页面录入各科目的考试成绩"
                                    font.pixelSize: 12
                                    color: "#6b7280"
                                }
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 60
                        color: "#f9fafb"
                        radius: 8

                        Row {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Rectangle {
                                width: 36
                                height: 36
                                radius: 18
                                color: "#f59e0b"
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: "3"
                                    color: "white"
                                    font.weight: Font.Bold
                                    anchors.centerIn: parent
                                }
                            }

                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                Text {
                                    text: "查看数据分析"
                                    font.weight: Font.Medium
                                    color: "#111827"
                                }
                                Text {
                                    text: "在数据分析页面查看成绩趋势和统计报告"
                                    font.pixelSize: 12
                                    color: "#6b7280"
                                }
                            }
                        }
                    }
                }
            }
        }

        standardButtons: Dialog.Close
    }

    // 常见问题对话框
    Dialog {
        id: faqDialog
        title: "常见问题"
        width: 600
        height: 500
        anchors.centerIn: parent
        modal: true

        ScrollView {
            anchors.fill: parent

            Column {
                width: parent.width
                spacing: 16

                Repeater {
                    model: [
                        {
                            question: "如何导入学生信息？",
                            answer: "您可以在导入导出页面选择'导入学生信息'，支持Excel和CSV格式文件。请确保文件格式符合模板要求。"
                        },
                        {
                            question: "成绩数据可以批量导入吗？",
                            answer: "是的，系统支持批量导入成绩数据。请在成绩管理页面点击'批量导入'按钮，下载模板后按格式填写数据。"
                        },
                        {
                            question: "如何设置自动备份？",
                            answer: "在备份恢复页面点击'自动备份设置'，可以设置备份频率、时间和保存位置。建议开启自动备份以保护数据安全。"
                        },
                        {
                            question: "忘记登录密码怎么办？",
                            answer: "请联系系统管理员重置密码，或使用密码找回功能（如果已设置安全邮箱）。"
                        },
                        {
                            question: "系统运行缓慢怎么办？",
                            answer: "请检查系统资源使用情况，清理不必要的数据，或联系技术支持进行系统优化。"
                        }
                    ]

                    delegate: Rectangle {
                        width: parent.width
                        height: questionColumn.height + 24
                        color: "#f9fafb"
                        radius: 8

                        Column {
                            id: questionColumn
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            Text {
                                text: "Q: " + modelData.question
                                font.weight: Font.Medium
                                color: "#111827"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }

                            Text {
                                text: "A: " + modelData.answer
                                color: "#6b7280"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }
                }
            }
        }

        standardButtons: Dialog.Close
    }

    // 联系支持对话框
    Dialog {
        id: contactSupportDialog
        title: "联系技术支持"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "请描述您遇到的问题，我们会尽快为您解决："
                font.weight: Font.Medium
                color: "#374151"
            }

            TextField {
                width: parent.width
                placeholderText: "问题标题"
            }

            ScrollView {
                width: parent.width
                height: 150

                TextArea {
                    placeholderText: "详细描述您遇到的问题..."
                    wrapMode: TextArea.Wrap
                }
            }

            Row {
                spacing: 8

                Text {
                    text: "联系方式:"
                    anchors.verticalCenter: parent.verticalCenter
                    font.weight: Font.Medium
                    color: "#374151"
                }

                TextField {
                    width: 200
                    placeholderText: "邮箱或电话"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            CheckBox {
                text: "允许收集系统信息以便诊断问题"
                checked: true
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 简化其他对话框定义...
    Dialog { id: featuresDialog; title: "功能介绍"; width: 600; height: 500; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Close }
    Dialog { id: changelogDialog; title: "更新日志"; width: 600; height: 500; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Close }
    Dialog { id: checkUpdateDialog; title: "检查更新"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Close }
    Dialog { id: systemDiagnosisDialog; title: "系统诊断"; width: 500; height: 400; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Close }
    Dialog { id: exportLogsDialog; title: "导出日志"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: featureSuggestionDialog; title: "功能建议"; width: 500; height: 400; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: bugReportDialog; title: "问题反馈"; width: 500; height: 400; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: surveyDialog; title: "用户体验调研"; width: 500; height: 400; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
}