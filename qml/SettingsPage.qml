import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: settingsPage
    
    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24
        
        // 页面标题
        Row {
            width: parent.width
            
            Column {
                Text {
                    text: "系统设置"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }
                
                Text {
                    text: "配置应用程序的各项设置"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }
        }
        
        // 应用信息
        Rectangle {
            width: parent.width
            height: 120
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1
            
            Row {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                Rectangle {
                    width: 80
                    height: 80
                    radius: 40
                    color: "#2563eb"
                    anchors.verticalCenter: parent.verticalCenter
                    
                    Text {
                        text: "📚"
                        font.pixelSize: 32
                        anchors.centerIn: parent
                    }
                }
                
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8
                    
                    Text {
                        text: controller.appName
                        font.pixelSize: 24
                        font.bold: true
                        color: "#111827"
                    }
                    
                    Text {
                        text: "版本 " + controller.appVersion
                        font.pixelSize: 14
                        color: "#6b7280"
                    }
                    
                    Text {
                        text: controller.appDescription
                        font.pixelSize: 12
                        color: "#9ca3af"
                    }
                }
            }
        }
        
        // 界面设置
        Rectangle {
            width: parent.width
            height: 300
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1
            
            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                Text {
                    text: "界面设置"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }
                
                // 主题设置
                Row {
                    width: parent.width
                    
                    Text {
                        text: "主题"
                        font.pixelSize: 14
                        color: "#374151"
                        width: 120
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    ComboBox {
                        id: themeCombo
                        width: 200
                        model: ["浅色主题", "深色主题", "跟随系统"]
                        currentIndex: 0
                        
                        onCurrentIndexChanged: {
                            var themes = ["light", "dark", "auto"]
                            controller.saveSettings("theme", themes[currentIndex])
                        }
                    }
                }
                
                // 语言设置
                Row {
                    width: parent.width
                    
                    Text {
                        text: "语言"
                        font.pixelSize: 14
                        color: "#374151"
                        width: 120
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    ComboBox {
                        id: languageCombo
                        width: 200
                        model: ["简体中文", "English"]
                        currentIndex: 0
                        
                        onCurrentIndexChanged: {
                            var languages = ["zh-CN", "en-US"]
                            controller.saveSettings("language", languages[currentIndex])
                        }
                    }
                }
                
                // 动画设置
                Row {
                    width: parent.width
                    
                    Text {
                        text: "动画效果"
                        font.pixelSize: 14
                        color: "#374151"
                        width: 120
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    Switch {
                        id: animationSwitch
                        checked: true
                        anchors.verticalCenter: parent.verticalCenter
                        
                        onCheckedChanged: {
                            controller.saveSettings("animations_enabled", checked)
                        }
                    }
                }
                
                // 窗口透明度
                Row {
                    width: parent.width
                    
                    Text {
                        text: "窗口透明度"
                        font.pixelSize: 14
                        color: "#374151"
                        width: 120
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    Slider {
                        id: opacitySlider
                        width: 200
                        from: 0.7
                        to: 1.0
                        value: 0.95
                        stepSize: 0.05
                        anchors.verticalCenter: parent.verticalCenter
                        
                        onValueChanged: {
                            controller.saveSettings("window_opacity", value)
                        }
                    }
                    
                    Text {
                        text: Math.round(opacitySlider.value * 100) + "%"
                        font.pixelSize: 12
                        color: "#6b7280"
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }
        
        // 数据设置
        Rectangle {
            width: parent.width
            height: 250
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1
            
            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                Text {
                    text: "数据设置"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }
                
                // 自动保存
                Row {
                    width: parent.width
                    
                    Text {
                        text: "自动保存"
                        font.pixelSize: 14
                        color: "#374151"
                        width: 120
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    Switch {
                        id: autoSaveSwitch
                        checked: true
                        anchors.verticalCenter: parent.verticalCenter
                        
                        onCheckedChanged: {
                            controller.saveSettings("auto_save_enabled", checked)
                        }
                    }
                    
                    Text {
                        text: "每5分钟自动保存数据"
                        font.pixelSize: 12
                        color: "#6b7280"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 16
                    }
                }
                
                // 数据备份
                Row {
                    width: parent.width
                    
                    Text {
                        text: "数据备份"
                        font.pixelSize: 14
                        color: "#374151"
                        width: 120
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    ComboBox {
                        id: backupCombo
                        width: 200
                        model: ["不备份", "仅数据", "完整备份"]
                        currentIndex: 1
                        
                        onCurrentIndexChanged: {
                            var backupTypes = ["none", "data_only", "full"]
                            controller.saveSettings("backup_type", backupTypes[currentIndex])
                        }
                    }
                }
                
                // 数据导出
                Row {
                    width: parent.width
                    spacing: 12
                    
                    Button {
                        text: "导出数据"
                        icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z'/%3E%3C/svg%3E"
                        onClicked: controller.exportData()
                    }
                    
                    Button {
                        text: "导入数据"
                        flat: true
                        icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z'/%3E%3C/svg%3E"
                        onClicked: {
                            console.log("导入数据")
                        }
                    }
                    
                    Button {
                        text: "重置数据"
                        flat: true
                        palette.buttonText: "#dc2626"
                        onClicked: resetDataDialog.open()
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
            border.width: 1
            
            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                Text {
                    text: "系统信息"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }
                
                Column {
                    width: parent.width
                    spacing: 8
                    
                    Row {
                        width: parent.width
                        
                        Text {
                            text: "应用版本:"
                            font.pixelSize: 14
                            color: "#6b7280"
                            width: 120
                        }
                        
                        Text {
                            text: controller.appVersion
                            font.pixelSize: 14
                            color: "#111827"
                        }
                    }
                    
                    Row {
                        width: parent.width
                        
                        Text {
                            text: "构建时间:"
                            font.pixelSize: 14
                            color: "#6b7280"
                            width: 120
                        }
                        
                        Text {
                            text: "2024-01-15 10:30:00"
                            font.pixelSize: 14
                            color: "#111827"
                        }
                    }
                    
                    Row {
                        width: parent.width
                        
                        Text {
                            text: "框架版本:"
                            font.pixelSize: 14
                            color: "#6b7280"
                            width: 120
                        }
                        
                        Text {
                            text: "Rinui 1.0.0 + PySide6"
                            font.pixelSize: 14
                            color: "#111827"
                        }
                    }
                }
                
                Row {
                    spacing: 12
                    
                    Button {
                        text: "检查更新"
                        onClicked: {
                            console.log("检查更新")
                        }
                    }
                    
                    Button {
                        text: "关于"
                        flat: true
                        onClicked: aboutDialog.open()
                    }
                }
            }
        }
    }
    
    // 重置数据确认对话框
    Dialog {
        id: resetDataDialog
        title: "重置数据"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 250
        
        Column {
            anchors.fill: parent
            spacing: 16
            
            Text {
                text: "⚠️ 警告"
                font.pixelSize: 18
                font.bold: true
                color: "#dc2626"
            }
            
            Text {
                text: "此操作将删除所有学生、班级、成就等数据，且不可撤销。\n\n请确认您已经备份了重要数据。"
                font.pixelSize: 14
                color: "#374151"
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            CheckBox {
                id: confirmCheckbox
                text: "我已了解风险，确认重置所有数据"
                font.pixelSize: 12
            }
        }
        
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        onAccepted: {
            if (confirmCheckbox.checked) {
                console.log("重置所有数据")
                confirmCheckbox.checked = false
            }
        }
        
        onRejected: {
            confirmCheckbox.checked = false
        }
    }
    
    // 关于对话框
    Dialog {
        id: aboutDialog
        title: "关于 " + controller.appName
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 300
        
        Column {
            anchors.fill: parent
            spacing: 16
            
            Text {
                text: "📚"
                font.pixelSize: 48
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Text {
                text: controller.appName
                font.pixelSize: 24
                font.bold: true
                color: "#111827"
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Text {
                text: "版本 " + controller.appVersion
                font.pixelSize: 14
                color: "#6b7280"
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Text {
                text: controller.appDescription
                font.pixelSize: 12
                color: "#9ca3af"
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            Text {
                text: "基于 Rinui 框架和 PySide6 构建\n\n© 2024 Prowaxw. All rights reserved."
                font.pixelSize: 11
                color: "#9ca3af"
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
            }
        }
        
        standardButtons: Dialog.Ok
    }
}