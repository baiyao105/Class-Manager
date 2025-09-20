import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import "./components"

FluentPage {
    id: classesPage
    horizontalPadding: 0
    verticalPadding: 0

    // 主容器 - 参考HTML的container样式
    Rectangle {
        anchors.fill: parent
        anchors.margins: 28
        radius: 18
        color: "#ffffff"
        border.width: 1
        border.color: "#e9ecef"

        Column {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 16

            // 顶部分段控制器
            Row {
                width: parent.width
                spacing: 16

                Rectangle {
                    id: segmentedControl
                    height: 40
                    width: 200
                    radius: 20
                    color: "#f8f9fa"
                    border.color: "#e9ecef"
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 4
                        spacing: 4

                        Button {
                            id: studentViewBtn
                            width: 92
                            height: 32
                            text: "学生视图"
                            flat: true
                            checkable: true
                            checked: true
                            
                            background: Rectangle {
                                radius: 16
                                color: parent.checked ? "#0078d4" : "transparent"
                                opacity: parent.checked ? 0.16 : 0
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.weight: Font.DemiBold
                                color: parent.checked ? "#0078d4" : "#6c757d"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: {
                                checked = true
                                groupViewBtn.checked = false
                                currentView = "student"
                                refreshView()
                            }
                        }

                        Button {
                            id: groupViewBtn
                            width: 92
                            height: 32
                            text: "班级视图"
                            flat: true
                            checkable: true
                            
                            background: Rectangle {
                                radius: 16
                                color: parent.checked ? "#0078d4" : "transparent"
                                opacity: parent.checked ? 0.16 : 0
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.weight: Font.DemiBold
                                color: parent.checked ? "#0078d4" : "#6c757d"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: {
                                checked = true
                                studentViewBtn.checked = false
                                currentView = "class"
                                refreshView()
                            }
                        }
                    }
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "演示班级"
                    color: "#6c757d"
                    font.weight: Font.DemiBold
                }
            }

            // 主要布局区域
            Row {
                width: parent.width
                height: parent.height - 120
                spacing: 16

                // 左侧主工作区
                Rectangle {
                    id: workArea
                    width: parent.width - 336
                    height: parent.height
                    radius: 12
                    color: "#fbfcfd"
                    border.color: "#e9ecef"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        // 工作区标题
                        Row {
                            width: parent.width
                            
                            Text {
                                text: currentView === "student" ? "学生列表" : "班级列表"
                                font.pixelSize: 16
                                font.weight: Font.Bold
                                color: "#212529"
                            }
                            
                            Text {
                                anchors.right: parent.right
                                text: currentView === "student" ? "当前：学生视图" : "当前：班级视图"
                                font.pixelSize: 13
                                color: "#6c757d"
                            }
                        }

                        // 卡片网格
                        ScrollView {
                            width: parent.width
                            height: parent.height - 40
                            clip: true

                            GridLayout {
                                id: cardGrid
                                width: workArea.width - 24
                                columns: Math.floor(width / 200)
                                columnSpacing: 12
                                rowSpacing: 12

                                Repeater {
                                    id: cardRepeater
                                    model: currentView === "student" ? studentModel : classModel

                                    Rectangle {
                                        Layout.preferredWidth: 180
                                        Layout.preferredHeight: 140
                                        radius: 12
                                        color: "#ffffff"
                                        border.color: "#e9ecef"
                                        border.width: 1

                                        // 悬停效果
                                        MouseArea {
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onEntered: {
                                                parent.border.color = "#0078d4"
                                                parent.y -= 6
                                            }
                                            onExited: {
                                                parent.border.color = "#e9ecef"
                                                parent.y += 6
                                            }
                                            onClicked: openDetailModal(modelData)
                                        }

                                        Column {
                                            anchors.fill: parent
                                            anchors.margins: 12
                                            spacing: 8

                                            Text {
                                                text: modelData.name || "未知"
                                                font.weight: Font.Bold
                                                color: "#212529"
                                                elide: Text.ElideRight
                                                width: parent.width
                                            }

                                            Text {
                                                text: currentView === "student" ? 
                                                      ("学号：" + (modelData.id || "")) :
                                                      ("成员：" + (modelData.studentCount || 0))
                                                font.pixelSize: 13
                                                color: "#6c757d"
                                            }

                                            Text {
                                                text: currentView === "student" ? 
                                                      ("学分：" + (modelData.credits || 0)) :
                                                      ("平均分：" + (modelData.avgScore || 0))
                                                font.pixelSize: 13
                                                color: "#6c757d"
                                            }

                                            Rectangle {
                                                width: parent.width
                                                height: 24
                                                radius: 12
                                                color: "#e3f2fd"
                                                
                                                Text {
                                                    anchors.centerIn: parent
                                                    text: currentView === "student" ? 
                                                          ("班级 " + (modelData.className || "A")) :
                                                          ("ID " + (modelData.id || ""))
                                                    color: "#0078d4"
                                                    font.weight: Font.DemiBold
                                                    font.pixelSize: 13
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
                    id: sidePanel
                    width: 320
                    height: parent.height
                    radius: 12
                    color: "#ffffff"
                    border.color: "#e9ecef"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        Row {
                            width: parent.width
                            
                            Text {
                                text: "快速班级信息"
                                font.weight: Font.Bold
                                color: "#212529"
                            }
                            
                            Text {
                                anchors.right: parent.right
                                text: "及时概览"
                                font.pixelSize: 13
                                color: "#6c757d"
                            }
                        }

                        // 标签页
                        Row {
                            width: parent.width
                            spacing: 8

                            Button {
                                id: tab1Btn
                                text: "概览"
                                flat: true
                                checkable: true
                                checked: true
                                width: (parent.width - 16) / 3
                                
                                background: Rectangle {
                                    radius: 8
                                    color: parent.checked ? "#e3f2fd" : "transparent"
                                }
                                
                                contentItem: Text {
                                    text: parent.text
                                    color: parent.checked ? "#0078d4" : "#6c757d"
                                    font.weight: Font.Bold
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                
                                onClicked: {
                                    checked = true
                                    tab2Btn.checked = false
                                    tab3Btn.checked = false
                                    currentTab = 1
                                }
                            }

                            Button {
                                id: tab2Btn
                                text: "成绩"
                                flat: true
                                checkable: true
                                width: (parent.width - 16) / 3
                                
                                background: Rectangle {
                                    radius: 8
                                    color: parent.checked ? "#e3f2fd" : "transparent"
                                }
                                
                                contentItem: Text {
                                    text: parent.text
                                    color: parent.checked ? "#0078d4" : "#6c757d"
                                    font.weight: Font.Bold
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                
                                onClicked: {
                                    checked = true
                                    tab1Btn.checked = false
                                    tab3Btn.checked = false
                                    currentTab = 2
                                }
                            }

                            Button {
                                id: tab3Btn
                                text: "更多"
                                flat: true
                                checkable: true
                                width: (parent.width - 16) / 3
                                
                                background: Rectangle {
                                    radius: 8
                                    color: parent.checked ? "#e3f2fd" : "transparent"
                                }
                                
                                contentItem: Text {
                                    text: parent.text
                                    color: parent.checked ? "#0078d4" : "#6c757d"
                                    font.weight: Font.Bold
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                
                                onClicked: {
                                    checked = true
                                    tab1Btn.checked = false
                                    tab2Btn.checked = false
                                    currentTab = 3
                                }
                            }
                        }

                        // 标签页内容
                        Rectangle {
                            width: parent.width
                            height: 160
                            radius: 10
                            color: "#fbfcfd"
                            border.color: "#e9ecef"
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8
                                visible: currentTab === 1

                                Text {
                                    text: "班级 A · 10 人"
                                    font.weight: Font.Bold
                                    color: "#212529"
                                }

                                Text {
                                    text: "平均学分：12.6"
                                    font.pixelSize: 13
                                    color: "#6c757d"
                                }

                                Row {
                                    spacing: 8
                                    
                                    Button {
                                        text: "查看"
                                        flat: true
                                        font.pixelSize: 12
                                        onClicked: console.log("查看班级详情")
                                    }
                                    
                                    Button {
                                        text: "导出"
                                        flat: true
                                        font.pixelSize: 12
                                        onClicked: console.log("导出班级报告")
                                    }
                                }
                            }

                            Column {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8
                                visible: currentTab === 2

                                Text {
                                    text: "成绩分布"
                                    font.weight: Font.Bold
                                    color: "#212529"
                                }

                                Text {
                                    text: "A: 3 / B: 4 / C: 3"
                                    font.pixelSize: 13
                                    color: "#6c757d"
                                }
                            }

                            Column {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8
                                visible: currentTab === 3

                                Text {
                                    text: "其他信息"
                                    font.weight: Font.Bold
                                    color: "#212529"
                                }

                                Text {
                                    text: "自定义备注 / 快捷设置"
                                    font.pixelSize: 13
                                    color: "#6c757d"
                                }
                            }
                        }
                    }
                }
            }

            // 底部工具栏区域
            Row {
                width: parent.width
                height: 64
                spacing: 12

                // 左侧工具栏
                Rectangle {
                    width: parent.width - 332
                    height: 64
                    radius: 12
                    color: "#f8f9fa"
                    border.color: "#e9ecef"
                    border.width: 1

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 8

                        Button {
                            text: "点名"
                            flat: true
                            font.weight: Font.DemiBold
                            onClicked: console.log("点名功能")
                        }

                        Button {
                            text: "群发"
                            flat: true
                            font.weight: Font.DemiBold
                            onClicked: console.log("群发消息")
                        }

                        Button {
                            text: "批量评分"
                            flat: true
                            font.weight: Font.DemiBold
                            onClicked: console.log("批量评分")
                        }
                    }

                    Row {
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 8

                        TextField {
                            id: toolInput
                            width: 180
                            placeholderText: "输入快捷按钮名字"
                            font.pixelSize: 12
                        }

                        Button {
                            text: "添加"
                            flat: true
                            font.weight: Font.DemiBold
                            onClicked: {
                                if (toolInput.text.trim()) {
                                    console.log("添加工具：" + toolInput.text)
                                    toolInput.clear()
                                }
                            }
                        }
                    }
                }

                // 右侧状态区域
                Rectangle {
                    width: 320
                    height: 64
                    radius: 12
                    color: "#ffffff"
                    border.color: "#e9ecef"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Text {
                            text: "卡片预览 · 快速操作"
                            font.weight: Font.Bold
                            color: "#212529"
                            font.pixelSize: 12
                        }

                        Text {
                            id: statusText
                            text: "选中项会显示在这里"
                            font.pixelSize: 11
                            color: "#6c757d"
                            elide: Text.ElideRight
                            width: parent.width
                        }
                    }
                }
            }
        }
    }

    // 详情模态框
    Dialog {
        id: detailModal
        modal: true
        anchors.centerIn: parent
        width: 360
        height: 300
        
        property var itemData: null

        background: Rectangle {
            radius: 14
            color: "#ffffff"
            border.color: "#e9ecef"
            border.width: 1
        }

        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Text {
                text: "详情"
                font.pixelSize: 18
                font.weight: Font.Bold
                color: "#212529"
            }

            Column {
                width: parent.width
                spacing: 8

                Text {
                    text: detailModal.itemData ? detailModal.itemData.name : ""
                    font.weight: Font.Bold
                    color: "#212529"
                }

                Text {
                    text: currentView === "student" ? 
                          ("学号：" + (detailModal.itemData ? detailModal.itemData.id : "")) :
                          ("成员数：" + (detailModal.itemData ? detailModal.itemData.studentCount : ""))
                    font.pixelSize: 13
                    color: "#6c757d"
                }

                Text {
                    text: currentView === "student" ? 
                          ("学分：" + (detailModal.itemData ? detailModal.itemData.credits : "")) :
                          ("平均分：" + (detailModal.itemData ? detailModal.itemData.avgScore : ""))
                    font.pixelSize: 13
                    color: "#6c757d"
                }
            }

            Row {
                spacing: 8
                
                Button {
                    text: currentView === "student" ? "发消息" : "成员列表"
                    flat: true
                    onClicked: {
                        console.log(currentView === "student" ? "发送消息" : "查看成员列表")
                        detailModal.close()
                    }
                }
                
                Button {
                    text: currentView === "student" ? "查看成绩" : "导出报表"
                    flat: true
                    onClicked: {
                        console.log(currentView === "student" ? "查看成绩" : "导出报表")
                        detailModal.close()
                    }
                }
            }

            Button {
                text: "关闭"
                anchors.right: parent.right
                flat: true
                onClicked: detailModal.close()
            }
        }
    }

    // 数据模型和状态
    property string currentView: "student"
    property int currentTab: 1

    property var studentModel: [
        {name: "学生 1", id: "100", credits: 25, className: "A"},
        {name: "学生 2", id: "101", credits: 28, className: "A"},
        {name: "学生 3", id: "102", credits: 22, className: "B"},
        {name: "学生 4", id: "103", credits: 30, className: "A"},
        {name: "学生 5", id: "104", credits: 26, className: "B"},
        {name: "学生 6", id: "105", credits: 24, className: "A"}
    ]

    property var classModel: [
        {name: "班级 1", id: "G1", studentCount: 4, avgScore: 12.5},
        {name: "班级 2", id: "G2", studentCount: 5, avgScore: 14.2},
        {name: "班级 3", id: "G3", studentCount: 3, avgScore: 11.3}
    ]

    function refreshView() {
        // 刷新视图逻辑
        console.log("切换到：" + currentView + " 视图")
    }

    function openDetailModal(data) {
        detailModal.itemData = data
        statusText.text = "已选：" + data.name + 
                         (currentView === "student" ? 
                          ("（学号 " + data.id + "）· 学分 " + data.credits) :
                          (" · 成员 " + data.studentCount))
        detailModal.open()
    }
}
