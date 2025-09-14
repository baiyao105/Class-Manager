import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: dashboardPage
    
    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24
        
        // 页面标题
        Row {
            width: parent.width
            
            Column {
                Text {
                    text: "仪表板"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }
                
                Text {
                    text: "班级管理系统概览"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }
        }
        
        // 统计卡片
        GridLayout {
            width: parent.width
            columns: 4
            columnSpacing: 16
            rowSpacing: 16
            
            StatCard {
                title: "学生总数"
                valueText: controller.stats.totalStudents.toString()
                subtitle: "活跃学生"
                themeColor: "#2563eb"
                icon: "👥"
            }
            
            StatCard {
                title: "班级数量"
                valueText: controller.stats.totalClasses.toString()
                subtitle: "活跃班级"
                themeColor: "#10b981"
                icon: "🏫"
            }
            
            StatCard {
                title: "成就获得"
                valueText: controller.stats.totalAchievements.toString()
                subtitle: "本月新增"
                themeColor: "#f59e0b"
                icon: "🏆"
            }
            
            StatCard {
                title: "平均分数"
                valueText: controller.stats.averageScore.toFixed(1)
                subtitle: "全校平均"
                themeColor: "#3b82f6"
                icon: "📊"
            }
        }
        
        // 图表和排名区域
        Row {
            width: parent.width
            spacing: 16
            
            // 分数趋势图表
            Rectangle {
                width: parent.width * 0.65
                height: 350
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"
                border.width: 1
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16
                    
                    Text {
                        text: "分数趋势"
                        font.pixelSize: 18
                        font.bold: true
                        color: "#111827"
                    }
                    
                    // 简单的趋势图表示
                    Rectangle {
                        width: parent.width
                        height: 250
                        color: "#f9fafb"
                        radius: 8
                        
                        Text {
                            anchors.centerIn: parent
                            text: "📈 分数趋势图表\n(集成图表库后显示)"
                            font.pixelSize: 14
                            color: "#6b7280"
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
            
            // 班级排名
            Rectangle {
                width: parent.width * 0.35 - 16
                height: 350
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
                        font.pixelSize: 18
                        font.bold: true
                        color: "#111827"
                    }
                    
                    ListView {
                        width: parent.width
                        height: 250
                        model: controller.classes
                        
                        delegate: Rectangle {
                            width: parent.width
                            height: 60
                            color: index % 2 === 0 ? "#f9fafb" : "transparent"
                            radius: 6
                            
                            Row {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12
                                
                                // 排名
                                Rectangle {
                                    width: 24
                                    height: 24
                                    radius: 12
                                    color: index === 0 ? "#fbbf24" : 
                                           index === 1 ? "#9ca3af" :
                                           index === 2 ? "#cd7f32" : "#e5e7eb"
                                    anchors.verticalCenter: parent.verticalCenter
                                    
                                    Text {
                                        text: (index + 1).toString()
                                        anchors.centerIn: parent
                                        font.pixelSize: 12
                                        font.bold: true
                                        color: index < 3 ? "white" : "#374151"
                                    }
                                }
                                
                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    
                                    Text {
                                        text: modelData.name
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "#111827"
                                    }
                                    
                                    Text {
                                        text: modelData.studentCount + "人 · 平均" + modelData.averageScore.toFixed(1) + "分"
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
        
        // 快速操作
        Rectangle {
            width: parent.width
            height: 120
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1
            
            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                Text {
                    text: "快速操作"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }
                
                Row {
                    spacing: 12
                    
                    Button {
                        text: "添加学生"
                        highlighted: true
                        icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E"
                        onClicked: addStudentDialog.open()
                    }
                    
                    Button {
                        text: "创建班级"
                        icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z'/%3E%3C/svg%3E"
                        onClicked: addClassDialog.open()
                    }
                    
                    Button {
                        text: "分数统计"
                        flat: true
                        icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E"
                        onClicked: controller.refreshStats()
                    }
                    
                    Button {
                        text: "导出数据"
                        flat: true
                        icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z'/%3E%3C/svg%3E"
                        onClicked: controller.exportData()
                    }
                }
            }
        }
    }
    
    // 添加学生对话框
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
                id: studentNameField
                width: parent.width
                placeholderText: "学生姓名"
            }
            
            TextField {
                id: studentNumberField
                width: parent.width
                placeholderText: "学号"
            }
            
            ComboBox {
                id: classComboBox
                width: parent.width
                model: controller.classes.map(c => c.name)
                displayText: "选择班级"
            }
        }
        
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        onAccepted: {
            if (studentNameField.text && studentNumberField.text && classComboBox.currentIndex >= 0) {
                controller.addStudent(
                    studentNameField.text,
                    studentNumberField.text,
                    controller.classes[classComboBox.currentIndex].name
                )
                studentNameField.clear()
                studentNumberField.clear()
                classComboBox.currentIndex = -1
            }
        }
    }
    
    // 添加班级对话框
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
                controller.addClass(classNameField.text, teacherNameField.text)
                classNameField.clear()
                teacherNameField.clear()
            }
        }
    }
}