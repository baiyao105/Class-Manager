import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ApplicationWindow {
    id: window
    width: 1200
    height: 800
    visible: true
    title: controller.appName + " v" + controller.appVersion

    property int currentPageIndex: 0

    // 主布局
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // 侧边导航栏
        Rectangle {
            Layout.preferredWidth: 250
            Layout.fillHeight: true
            color: "#f8f9fa"
            border.color: "#e9ecef"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                // 应用标题
                Text {
                    text: controller.appName
                    font.pixelSize: 24
                    font.bold: true
                    color: "#2563eb"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: "v" + controller.appVersion
                    font.pixelSize: 12
                    color: "#6b7280"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: "#e5e7eb"
                    anchors.margins: 8
                }

                // 导航按钮
                NavigationButton {
                    text: "仪表板"
                    icon: "📊"
                    isSelected: currentPageIndex === 0
                    onClicked: currentPageIndex = 0
                }

                NavigationButton {
                    text: "学生管理"
                    icon: "👥"
                    isSelected: currentPageIndex === 1
                    onClicked: currentPageIndex = 1
                }

                NavigationButton {
                    text: "班级管理"
                    icon: "🏫"
                    isSelected: currentPageIndex === 2
                    onClicked: currentPageIndex = 2
                }

                NavigationButton {
                    text: "成就系统"
                    icon: "🏆"
                    isSelected: currentPageIndex === 3
                    onClicked: currentPageIndex = 3
                }

                NavigationButton {
                    text: "系统设置"
                    icon: "⚙️"
                    isSelected: currentPageIndex === 4
                    onClicked: currentPageIndex = 4
                }
            }
        }

        // 主内容区域
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ffffff"

            StackLayout {
                id: stackLayout
                anchors.fill: parent
                currentIndex: currentPageIndex

                // 仪表板页面
                DashboardPage {
                    id: dashboardPage
                }

                // 学生管理页面
                StudentsPage {
                    id: studentsPage
                }

                // 班级管理页面
                ClassesPage {
                    id: classesPage
                }

                // 成就系统页面
                AchievementsPage {
                    id: achievementsPage
                }

                // 设置页面
                SettingsPage {
                    id: settingsPage
                }
            }
        }
    }
}
