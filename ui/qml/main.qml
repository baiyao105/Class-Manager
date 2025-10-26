import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentWindow {
    id: window
    visible: true
    title: qsTr("班级管理系统 v2.0.0")
    width: 1200
    height: 800
    minimumWidth: 800
    minimumHeight: 600

    // 导航项配置 - 设置 主页(1.html) 为首页
    navigationItems: [
        {
            title: qsTr("主页"),
            page: Qt.resolvedUrl("HomePage.qml"),
            icon: "ic_fluent_home_20_regular"
        },
        {
            title: qsTr("班级管理"),
            page: Qt.resolvedUrl("ClassPage.qml"),
            icon: "ic_fluent_building_20_regular"
        },
        {
            title: qsTr("学生管理"),
            page: Qt.resolvedUrl("StudentsPage.qml"),
            icon: "ic_fluent_people_20_regular"
        },
        {
            title: qsTr("积分管理"),
            page: Qt.resolvedUrl("ScoreManagementPage.qml"),
            icon: "ic_fluent_chart_multiple_20_regular"
        },
        {
            title: qsTr("数据分析"),
            page: Qt.resolvedUrl("DataAnalysisPage.qml"),
            icon: "ic_fluent_data_bar_chart_20_regular"
        },
        {
            title: qsTr("设置"),
            page: Qt.resolvedUrl("SettingsPage.qml"),
            icon: "ic_fluent_settings_20_regular"
        }
    ]

    // 全局快捷键 - 使用data属性，更新快捷键映射
    data: [
        Shortcut {
            sequence: "Ctrl+1"
            onActivated: currentPageIndex = 0  // 主页
        },
        Shortcut {
            sequence: "Ctrl+2"
            onActivated: currentPageIndex = 1  // 班级管理
        },
        Shortcut {
            sequence: "Ctrl+3"
            onActivated: currentPageIndex = 2  // 学生管理
        },
        Shortcut {
            sequence: "Ctrl+4"
            onActivated: currentPageIndex = 3  // 积分管理
        },
        Shortcut {
            sequence: "Ctrl+5"
            onActivated: currentPageIndex = 4  // 数据分析
        },
        Shortcut {
            sequence: "Ctrl+6"
            onActivated: currentPageIndex = 5  // 设置
        },
        Shortcut {
            sequence: "Ctrl+B"
            onActivated: navigationView.navigationBar.collapsed = !navigationView.navigationBar.collapsed
        }
    ]
}
