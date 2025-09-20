import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

// ContentSection - 内容区块组件
Rectangle {
    id: contentSection
    
    // 区块属性
    property string sectionTitle: ""
    property string sectionSubtitle: ""
    property alias sectionActions: sectionActionsRow.children
    property alias content: contentArea.children
    property bool collapsible: false
    property bool collapsed: false
    property color backgroundColor: "#ffffff"
    property color borderColor: "#e5e7eb"
    
    width: parent.width
    height: collapsed ? headerArea.height : (headerArea.height + contentArea.height + 32)
    color: backgroundColor
    radius: 12
    border.color: borderColor
    border.width: 1
    
    // 动画效果
    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }
    
    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16
        
        // 区块头部
        Rectangle {
            id: headerArea
            width: parent.width
            height: Math.max(headerContent.height, 40)
            color: "transparent"
            
            Row {
                id: headerContent
                width: parent.width
                spacing: 16
                
                // 标题区域
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2
                    width: parent.width - sectionActionsRow.width - collapseButton.width - 32
                    
                    Text {
                        text: sectionTitle
                        font.pixelSize: 18
                        font.weight: Font.Medium
                        color: "#111827"
                        visible: sectionTitle !== ""
                    }
                    
                    Text {
                        text: sectionSubtitle
                        font.pixelSize: 14
                        color: "#6b7280"
                        visible: sectionSubtitle !== ""
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }
                }
                
                // 弹性空间
                Item { Layout.fillWidth: true }
                
                // 区块操作按钮
                Row {
                    id: sectionActionsRow
                    spacing: 8
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                // 折叠按钮
                Button {
                    id: collapseButton
                    width: 32
                    height: 32
                    visible: collapsible
                    flat: true
                    anchors.verticalCenter: parent.verticalCenter
                    
                    contentItem: Text {
                        text: collapsed ? "▼" : "▲"
                        font.pixelSize: 12
                        color: "#6b7280"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        collapsed = !collapsed
                    }
                    
                    background: Rectangle {
                        color: parent.hovered ? "#f3f4f6" : "transparent"
                        radius: 6
                    }
                }
            }
        }
        
        // 内容区域
        Column {
            id: contentArea
            width: parent.width
            spacing: 16
            visible: !collapsed
            opacity: collapsed ? 0 : 1
            
            Behavior on opacity {
                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
            }
        }
    }
    
    // 区块状态
    states: [
        State {
            name: "collapsed"
            when: collapsed
            PropertyChanges { target: contentArea; visible: false }
        },
        State {
            name: "expanded"
            when: !collapsed
            PropertyChanges { target: contentArea; visible: true }
        }
    ]
    
    // 区块方法
    function toggleCollapse() {
        if (collapsible) {
            collapsed = !collapsed
        }
    }
    
    function expand() {
        if (collapsible) {
            collapsed = false
        }
    }
    
    function collapse() {
        if (collapsible) {
            collapsed = true
        }
    }
}