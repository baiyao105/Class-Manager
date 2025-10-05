import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import "./components"

FluentPage {
    id: studentsPage
    title: qsTr("学生管理")
    horizontalPadding: 24
    verticalPadding: 24

    // 页面头部工具栏
    contentHeader: Item {
        width: parent.width
        height: 80

        Rectangle {
            anchors.fill: parent
            color: "white"
            radius: 8
            border.color: "#e5e7eb"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                // 搜索框
                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: qsTr("搜索学生姓名、学号...")
                    leftPadding: 40

                    Rectangle {
                        anchors.left: parent.left
                        anchors.leftMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        width: 16
                        height: 16
                        color: "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "\ue721"  // 使用Fluent图标字体
                            font.family: "Segoe Fluent Icons"
                            font.pixelSize: 14
                            color: "#6b7280"
                        }
                    }

                    onTextChanged: {
                        if (controller) {
                            controller.filterStudents(text)
                        }
                    }
                }

                // 添加学生按钮
                Button {
                    text: qsTr("添加学生")
                    icon.name: "ic_fluent_person_add_20_regular"
                    onClicked: addStudentDialog.open()
                }

                // 批量操作按钮
                Button {
                    text: qsTr("批量操作")
                    icon.name: "ic_fluent_select_all_on_20_regular"
                    enabled: false  // 当选中学生时启用
                }
            }
        }
    }
                    }
                }
            }

            // 添加学生按钮
            Button {
                text: qsTr("添加学生")
                icon.name: "ic_fluent_person_add_20_regular"
                onClicked: addStudentDialog.open()
            }

            // 批量导入按钮
            Button {
                text: qsTr("批量导入")
                icon.name: "ic_fluent_document_arrow_up_20_regular"
                onClicked: importDialog.open()
            }
        }
    }

    // 学生列表
    ListView {
        id: studentsList
        width: parent.width
        height: parent.height - 100
        spacing: 12
        model: controller ? controller.students : []

        delegate: Rectangle {
            width: studentsList.width
            height: 120
            radius: 8
            color: "white"
            border.color: "#e5e7eb"
            border.width: 1

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: parent.color = "#f9fafb"
                onExited: parent.color = "white"
                onClicked: {
                    // 显示学生详情
                    studentDetailDialog.student = modelData
                    studentDetailDialog.open()
                }
            }

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                // 学生头像
                Rectangle {
                    Layout.preferredWidth: 60
                    Layout.preferredHeight: 60
                    radius: 30
                    color: "#f3f4f6"

                    Text {
                        anchors.centerIn: parent
                        text: modelData && modelData.name ? modelData.name.charAt(0) : "?"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#6b7280"
                    }
                }

                // 学生信息
                Column {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                        text: modelData ? modelData.name : "未知学生"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#1f2937"
                    }

                    Text {
                        text: qsTr("学号: ") + (modelData ? modelData.student_id : "")
                        font.pixelSize: 14
                        color: "#6b7280"
                    }

                    Text {
                        text: qsTr("班级: ") + (modelData ? modelData.class_name : "未分配")
                        font.pixelSize: 14
                        color: "#6b7280"
                    }
                }

                // 状态标签
                Rectangle {
                    Layout.preferredWidth: 60
                    Layout.preferredHeight: 24
                    radius: 12
                    color: modelData && modelData.is_active ? "#dcfce7" : "#fee2e2"

                    Text {
                        anchors.centerIn: parent
                        text: modelData && modelData.is_active ? qsTr("活跃") : qsTr("非活跃")
                        font.pixelSize: 12
                        color: modelData && modelData.is_active ? "#16a34a" : "#dc2626"
                    }
                }

                // 操作按钮
                Row {
                    spacing: 8

                    Button {
                        width: 32
                        height: 32
                        text: "✏️"
                        onClicked: {
                            editStudentDialog.student = modelData
                            editStudentDialog.open()
                        }
                    }

                    Button {
                        width: 32
                        height: 32
                        text: "🗑️"
                        onClicked: {
                            deleteConfirmDialog.student = modelData
                            deleteConfirmDialog.open()
                        }
                    }
                }
            }
        }

        // 空状态
        Rectangle {
            visible: studentsList.count === 0
            anchors.centerIn: parent
            width: 300
            height: 200
            color: "transparent"

            Column {
                anchors.centerIn: parent
                spacing: 16

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "📚"
                    font.pixelSize: 48
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("暂无学生数据")
                    font.pixelSize: 18
                    color: "#6b7280"
                }

                Button {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("添加第一个学生")
                    onClicked: addStudentDialog.open()
                }
            }
        }
    }

    // 添加学生对话框
    Dialog {
        id: addStudentDialog
        title: qsTr("添加学生")
        width: 400
        height: 300
        modal: true
        anchors.centerIn: parent

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            TextField {
                id: nameField
                width: parent.width
                placeholderText: qsTr("学生姓名")
            }

            TextField {
                id: studentIdField
                width: parent.width
                placeholderText: qsTr("学号")
            }

            ComboBox {
                id: classComboBox
                width: parent.width
                model: controller ? controller.classes : []
                textRole: "name"
                displayText: qsTr("选择班级")
            }

            Row {
                anchors.right: parent.right
                spacing: 12

                Button {
                    text: qsTr("取消")
                    onClicked: addStudentDialog.close()
                }

                Button {
                    text: qsTr("添加")
                    onClicked: {
                        if (controller) {
                            controller.addStudent(nameField.text, studentIdField.text, classComboBox.currentValue)
                        }
                        addStudentDialog.close()
                    }
                }
            }
        }
    }

    // 其他对话框占位符
    Dialog {
        id: editStudentDialog
        property var student
        title: qsTr("编辑学生")
        // 编辑学生的具体实现
    }

    Dialog {
        id: studentDetailDialog
        property var student
        title: qsTr("学生详情")
        // 学生详情的具体实现
    }

    Dialog {
        id: deleteConfirmDialog
        property var student
        title: qsTr("确认删除")
        // 删除确认的具体实现
    }

    Dialog {
        id: importDialog
        title: qsTr("批量导入")
        // 批量导入的具体实现
    }
}
