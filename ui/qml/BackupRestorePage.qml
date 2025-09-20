import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: backupRestorePage

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
                    text: "备份恢复"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "保护您的数据安全，支持自动备份和一键恢复"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }

            Item { Layout.fillWidth: true }

            Row {
                spacing: 12
                anchors.verticalCenter: parent.verticalCenter

                Button {
                    text: "立即备份"
                    highlighted: true
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z'/%3E%3Cpolyline points='14,2 14,8 20,8'/%3E%3C/svg%3E"
                    onClicked: createBackupDialog.open()
                }

                Button {
                    text: "恢复数据"
                    icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8'/%3E%3Cpath d='M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16'/%3E%3Cpolyline points='21,8 21,3 16,3'/%3E%3Cpolyline points='3,16 3,21 8,21'/%3E%3C/svg%3E"
                    onClicked: restoreDataDialog.open()
                }
            }
        }

        // 备份状态概览
        Row {
            width: parent.width
            spacing: 16

            StatCard {
                title: "最近备份"
                value: "2小时前"
                subtitle: "2024-01-15 12:30"
                icon: "💾"
                color: "#10b981"
                width: (parent.width - 48) / 4
            }

            StatCard {
                title: "备份总数"
                value: "24"
                subtitle: "本月新增 8 个"
                icon: "📦"
                color: "#3b82f6"
                width: (parent.width - 48) / 4
            }

            StatCard {
                title: "存储空间"
                value: "2.3GB"
                subtitle: "剩余 15.7GB"
                icon: "💿"
                color: "#f59e0b"
                width: (parent.width - 48) / 4
            }

            StatCard {
                title: "自动备份"
                value: "已启用"
                subtitle: "每日 02:00"
                icon: "⚙️"
                color: "#8b5cf6"
                width: (parent.width - 48) / 4
            }
        }

        // 快速操作
        Row {
            width: parent.width
            spacing: 16

            // 创建备份
            Rectangle {
                width: (parent.width - 32) / 3
                height: 180
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
                                text: "💾"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "创建备份"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "手动创建数据备份"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "完整备份"
                            width: parent.width
                            onClicked: createFullBackupDialog.open()
                        }

                        Button {
                            text: "增量备份"
                            width: parent.width
                            onClicked: createIncrementalBackupDialog.open()
                        }

                        Button {
                            text: "自定义备份"
                            width: parent.width
                            onClicked: createCustomBackupDialog.open()
                        }
                    }
                }
            }

            // 恢复数据
            Rectangle {
                width: (parent.width - 32) / 3
                height: 180
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
                                text: "🔄"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "恢复数据"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "从备份恢复数据"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "完整恢复"
                            width: parent.width
                            onClicked: fullRestoreDialog.open()
                        }

                        Button {
                            text: "选择性恢复"
                            width: parent.width
                            onClicked: selectiveRestoreDialog.open()
                        }

                        Button {
                            text: "从文件恢复"
                            width: parent.width
                            onClicked: fileRestoreDialog.open()
                        }
                    }
                }
            }

            // 备份设置
            Rectangle {
                width: (parent.width - 32) / 3
                height: 180
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
                                text: "⚙️"
                                font.pixelSize: 20
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "备份设置"
                                font.pixelSize: 18
                                font.weight: Font.Medium
                                color: "#111827"
                            }
                            Text {
                                text: "配置自动备份策略"
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: 8

                        Button {
                            text: "自动备份设置"
                            width: parent.width
                            onClicked: autoBackupSettingsDialog.open()
                        }

                        Button {
                            text: "存储位置设置"
                            width: parent.width
                            onClicked: storageSettingsDialog.open()
                        }

                        Button {
                            text: "清理旧备份"
                            width: parent.width
                            onClicked: cleanupDialog.open()
                        }
                    }
                }
            }
        }

        // 备份历史记录
        Rectangle {
            width: parent.width
            height: 450
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"

            Column {
                anchors.fill: parent
                anchors.margins: 20

                Row {
                    width: parent.width
                    Text {
                        text: "备份历史"
                        font.pixelSize: 18
                        font.weight: Font.Medium
                        color: "#111827"
                    }

                    Item { Layout.fillWidth: true }

                    Row {
                        spacing: 8

                        ComboBox {
                            model: ["全部类型", "完整备份", "增量备份", "自定义备份"]
                            width: 120
                            height: 32
                        }

                        Button {
                            text: "刷新"
                            height: 32
                        }
                    }
                }

                // 备份列表
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
                                    text: "备份时间"
                                    width: 140
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "备份类型"
                                    width: 100
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "备份名称"
                                    width: 200
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: "文件大小"
                                    width: 100
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
                                    text: "操作"
                                    Layout.fillWidth: true
                                    font.weight: Font.Medium
                                    color: "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }
                        }

                        // 备份记录列表
                        ScrollView {
                            width: parent.width
                            height: parent.height - 40
                            clip: true

                            ListView {
                                model: [
                                    {
                                        time: "2024-01-15 12:30:15",
                                        type: "完整备份",
                                        name: "auto_backup_20240115_1230",
                                        size: "156.8 MB",
                                        status: "完成"
                                    },
                                    {
                                        time: "2024-01-15 02:00:00",
                                        type: "自动备份",
                                        name: "auto_backup_20240115_0200",
                                        size: "145.2 MB",
                                        status: "完成"
                                    },
                                    {
                                        time: "2024-01-14 18:45:30",
                                        type: "增量备份",
                                        name: "incremental_backup_20240114",
                                        size: "23.4 MB",
                                        status: "完成"
                                    },
                                    {
                                        time: "2024-01-14 02:00:00",
                                        type: "自动备份",
                                        name: "auto_backup_20240114_0200",
                                        size: "142.8 MB",
                                        status: "完成"
                                    },
                                    {
                                        time: "2024-01-13 15:20:45",
                                        type: "自定义备份",
                                        name: "custom_backup_students_only",
                                        size: "45.6 MB",
                                        status: "完成"
                                    },
                                    {
                                        time: "2024-01-13 02:00:00",
                                        type: "自动备份",
                                        name: "auto_backup_20240113_0200",
                                        size: "138.9 MB",
                                        status: "失败"
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
                                            width: 140
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
                                                width: 80
                                                height: 24
                                                radius: 12
                                                color: {
                                                    switch(modelData.type) {
                                                        case "完整备份": return "#dcfce7"
                                                        case "增量备份": return "#dbeafe"
                                                        case "自动备份": return "#fef3c7"
                                                        case "自定义备份": return "#f3e8ff"
                                                        default: return "#f3f4f6"
                                                    }
                                                }
                                                anchors.centerIn: parent

                                                Text {
                                                    text: modelData.type
                                                    anchors.centerIn: parent
                                                    font.pixelSize: 10
                                                    color: {
                                                        switch(modelData.type) {
                                                            case "完整备份": return "#166534"
                                                            case "增量备份": return "#1d4ed8"
                                                            case "自动备份": return "#92400e"
                                                            case "自定义备份": return "#7c3aed"
                                                            default: return "#6b7280"
                                                        }
                                                    }
                                                }
                                            }
                                        }

                                        Text {
                                            text: modelData.name
                                            width: 200
                                            font.pixelSize: 12
                                            color: "#111827"
                                            anchors.verticalCenter: parent.verticalCenter
                                            elide: Text.ElideRight
                                        }

                                        Text {
                                            text: modelData.size
                                            width: 100
                                            font.pixelSize: 12
                                            color: "#6b7280"
                                            anchors.verticalCenter: parent.verticalCenter
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
                                                color: modelData.status === "完成" ? "#dcfce7" : "#fee2e2"
                                                anchors.centerIn: parent

                                                Text {
                                                    text: modelData.status
                                                    anchors.centerIn: parent
                                                    font.pixelSize: 12
                                                    color: modelData.status === "完成" ? "#166534" : "#dc2626"
                                                }
                                            }
                                        }

                                        Row {
                                            Layout.fillWidth: true
                                            spacing: 8
                                            anchors.verticalCenter: parent.verticalCenter

                                            Button {
                                                text: "恢复"
                                                height: 28
                                                width: 50
                                                font.pixelSize: 12
                                                enabled: modelData.status === "完成"
                                            }

                                            Button {
                                                text: "下载"
                                                height: 28
                                                width: 50
                                                font.pixelSize: 12
                                                enabled: modelData.status === "完成"
                                            }

                                            Button {
                                                text: "删除"
                                                height: 28
                                                width: 50
                                                font.pixelSize: 12
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
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 创建备份对话框
    Dialog {
        id: createBackupDialog
        title: "创建备份"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true

        Column {
            anchors.fill: parent
            spacing: 16

            Text {
                text: "选择备份类型和内容"
                font.weight: Font.Medium
                color: "#374151"
            }

            // 备份类型选择
            Column {
                width: parent.width
                spacing: 8

                RadioButton {
                    text: "完整备份 - 备份所有数据和设置"
                    checked: true
                }

                RadioButton {
                    text: "增量备份 - 仅备份自上次备份后的更改"
                }

                RadioButton {
                    text: "自定义备份 - 选择特定数据进行备份"
                }
            }

            // 备份内容选择
            Text {
                text: "备份内容"
                font.weight: Font.Medium
                color: "#374151"
            }

            Column {
                width: parent.width
                spacing: 8

                CheckBox {
                    text: "学生信息"
                    checked: true
                }

                CheckBox {
                    text: "成绩数据"
                    checked: true
                }

                CheckBox {
                    text: "班级信息"
                    checked: true
                }

                CheckBox {
                    text: "系统设置"
                    checked: true
                }

                CheckBox {
                    text: "用户配置"
                    checked: false
                }
            }

            // 备份位置
            Row {
                width: parent.width
                spacing: 16

                Text {
                    text: "备份位置:"
                    anchors.verticalCenter: parent.verticalCenter
                    font.weight: Font.Medium
                    color: "#374151"
                }

                TextField {
                    text: "D:/Backups/ClassManager/"
                    Layout.fillWidth: true
                    anchors.verticalCenter: parent.verticalCenter
                }

                Button {
                    text: "浏览"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 其他对话框...
    Dialog {
        id: restoreDataDialog
        title: "恢复数据"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    Dialog {
        id: autoBackupSettingsDialog
        title: "自动备份设置"
        width: 500
        height: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    // 简化其他对话框定义...
    Dialog { id: createFullBackupDialog; title: "完整备份"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: createIncrementalBackupDialog; title: "增量备份"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: createCustomBackupDialog; title: "自定义备份"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: fullRestoreDialog; title: "完整恢复"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: selectiveRestoreDialog; title: "选择性恢复"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: fileRestoreDialog; title: "从文件恢复"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: storageSettingsDialog; title: "存储位置设置"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
    Dialog { id: cleanupDialog; title: "清理旧备份"; width: 400; height: 300; anchors.centerIn: parent; modal: true; standardButtons: Dialog.Ok | Dialog.Cancel }
}