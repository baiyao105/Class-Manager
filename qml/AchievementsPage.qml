import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: achievementsPage
    
    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24
        
        // 页面标题
        Row {
            width: parent.width
            
            Column {
                Text {
                    text: "成就系统"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }
                
                Text {
                    text: "管理成就模板和学生成就记录"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }
        }
        
        // 成就统计
        GridLayout {
            width: parent.width
            columns: 4
            columnSpacing: 16
            rowSpacing: 16
            
            StatCard {
                title: "成就模板"
                valueText: "12"
                subtitle: "已创建"
                themeColor: "#8b5cf6"
                icon: "🏆"
            }
            
            StatCard {
                title: "获得成就"
                valueText: "342"
                subtitle: "总计"
                themeColor: "#f59e0b"
                icon: "⭐"
            }
            
            StatCard {
                title: "本月新增"
                valueText: "45"
                subtitle: "成就获得"
                themeColor: "#10b981"
                icon: "📈"
            }
            
            StatCard {
                title: "活跃学生"
                valueText: "89"
                subtitle: "有成就记录"
                themeColor: "#3b82f6"
                icon: "👥"
            }
        }
        
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
                            console.log("打开成就模板管理")
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
                            console.log("打开学生成就查看")
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
                    text: "最近获得的成就"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#111827"
                }
                
                ListView {
                    width: parent.width
                    height: 220
                    
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
    }
}