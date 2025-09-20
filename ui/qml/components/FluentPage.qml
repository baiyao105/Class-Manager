import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

// FluentPage - 统一的页面容器组件
ScrollView {
    id: fluentPage
    
    // 页面属性
    property string pageTitle: ""
    property string pageSubtitle: ""
    property alias headerActions: headerActionsRow.children
    property alias content: contentColumn.children
    property alias quickActions: quickActionsRow.children
    property alias statusCards: statusCardsGrid.children
    property alias mainContent: mainContentArea.children
    property alias bottomActions: bottomActionsRow.children
    
    // 页面配置
    property bool showQuickActions: true
    property bool showStatusCards: true
    property bool showBottomActions: false
    property int statusCardsColumns: 4
    property color backgroundColor: "#f8fafc"
    
    // 内容区域
    Rectangle {
        width: parent.width
        height: Math.max(parent.height, contentColumn.height + 48)
        color: backgroundColor
        
        Column {
            id: contentColumn
            width: parent.width - 48
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 24
            spacing: 24
            
            // 页面头部
            Rectangle {
                width: parent.width
                height: Math.max(headerContent.height, 80)
                color: "transparent"
                
                Row {
                    id: headerContent
                    width: parent.width
                    spacing: 16
                    
                    // 标题区域
                    Column {
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 4
                        
                        Text {
                            text: pageTitle
                            font.pixelSize: 32
                            font.bold: true
                            color: "#111827"
                            visible: pageTitle !== ""
                        }
                        
                        Text {
                            text: pageSubtitle
                            font.pixelSize: 16
                            color: "#6b7280"
                            visible: pageSubtitle !== ""
                        }
                    }
                    
                    // 弹性空间
                    Item { 
                        Layout.fillWidth: true 
                        width: parent.width - headerContent.width - headerActionsRow.width - 32
                    }
                    
                    // 头部操作按钮
                    Row {
                        id: headerActionsRow
                        spacing: 12
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
            
            // 状态卡片区域
            GridLayout {
                id: statusCardsGrid
                width: parent.width
                columns: statusCardsColumns
                columnSpacing: 16
                rowSpacing: 16
                visible: showStatusCards && children.length > 0
            }
            
            // 快速操作区域
            Rectangle {
                width: parent.width
                height: quickActionsContent.height + 40
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"
                border.width: 1
                visible: showQuickActions && quickActionsRow.children.length > 0
                
                Row {
                    id: quickActionsContent
                    anchors.centerIn: parent
                    spacing: 24
                    
                    Row {
                        id: quickActionsRow
                        spacing: 16
                    }
                }
            }
            
            // 主内容区域
            Column {
                id: mainContentArea
                width: parent.width
                spacing: 24
            }
            
            // 底部操作区域
            Rectangle {
                width: parent.width
                height: bottomActionsContent.height + 32
                color: "#ffffff"
                radius: 12
                border.color: "#e5e7eb"
                border.width: 1
                visible: showBottomActions && bottomActionsRow.children.length > 0
                
                Row {
                    id: bottomActionsContent
                    anchors.centerIn: parent
                    spacing: 16
                    
                    Row {
                        id: bottomActionsRow
                        spacing: 12
                    }
                }
            }
        }
    }
    
    // 页面动画效果
    Behavior on opacity {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }
    
    // 页面生命周期方法
    signal pageActivated()
    signal pageDeactivated()
    
    function refreshPage() {
        // 刷新页面数据的方法，子页面可以重写
    }
    
    function resetPage() {
        // 重置页面状态的方法，子页面可以重写
    }
}