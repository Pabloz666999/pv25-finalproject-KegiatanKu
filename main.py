import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QDateEdit, QAction, QFileDialog, QMessageBox, QStatusBar, QHBoxLayout, QComboBox, QHeaderView
)
from PyQt5.QtCore import QDate

DATABASE = "KegiatanKu.db"

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kegiatan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            lokasi TEXT,
            tanggal TEXT,
            status TEXT,
            catatan TEXT
        )
    ''')
    conn.commit()
    conn.close()

class KegiatanKu(QMainWindow):
    def __init__(self):
        super().__init__()
        create_table() 
        self.setWindowTitle("KegiatanKu - Organizer Kegiatan")
        self.setGeometry(100, 100, 800, 900)
        self.initUI()

    def initUI(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        export_csv_action = QAction("Export ke CSV", self)
        export_csv_action.triggered.connect(self.export_csv)
        fileMenu.addAction(export_csv_action)

        export_pdf_action = QAction("Export ke PDF", self)
        export_pdf_action.triggered.connect(self.export_pdf)
        fileMenu.addAction(export_pdf_action)

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        helpMenu = menubar.addMenu("Help")

        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(lambda: QMessageBox.information(
            self, "About", "KegiatanKu App\nBy: M. Bayu Aji - F1D02310144"))
        helpMenu.addAction(aboutAction)

        statusbar = QStatusBar()
        statusbar.showMessage("M. Bayu Aji | F1D02310144")
        self.setStatusBar(statusbar)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        form_layout = QGridLayout()

        self.input_judul = QLineEdit()
        self.input_lokasi = QLineEdit()
        self.input_status = QComboBox()
        self.input_status.addItems(["Akan Datang", "Sedang Berlangsung", "Selesai", "Dibatalkan"])
        self.input_catatan = QTextEdit()

        self.input_tanggal = QDateEdit()
        self.input_tanggal.setDisplayFormat("yyyy-MM-dd")
        self.input_tanggal.setCalendarPopup(True)
        self.input_tanggal.setDate(QDate())  
        self.input_tanggal.clear()           


        form_layout.addWidget(QLabel("Judul Kegiatan:"), 0, 0)
        form_layout.addWidget(self.input_judul, 0, 1)
        form_layout.addWidget(QLabel("Lokasi:"), 0, 2)
        form_layout.addWidget(self.input_lokasi, 0, 3)
        form_layout.addWidget(QLabel("Tanggal:"), 1, 0)
        form_layout.addWidget(self.input_tanggal, 1, 1)
        form_layout.addWidget(QLabel("Status:"), 1, 2)
        form_layout.addWidget(self.input_status, 1, 3)
        form_layout.addWidget(QLabel("Catatan:"), 2, 0)
        form_layout.addWidget(self.input_catatan, 2, 1, 2, 3)

        layout.addLayout(form_layout) 

        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.simpan_kegiatan)
        button_layout.addWidget(self.save_btn)

        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update_kegiatan)
        button_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Hapus")
        self.delete_btn.clicked.connect(self.hapus_kegiatan)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)


        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Judul", "Lokasi", "Tanggal", "Status", "Catatan"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.barisklik)
        layout.addWidget(self.table)


        central_widget.setLayout(layout)
        self.load_data()

        self.setStyleSheet("""
            QWidget {
                background-color: #212121;
                color: #e5e5e5;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }
            QPushButton {
                padding: 8px;
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005F9E;
            }
            QLabel {
                font-weight: 600;
                color: #e5e5e5;;
            }
            QLineEdit, QDateEdit, QTextEdit {
                background-color: #1a1a1a;
                color: #e5e5e5;
                border: 1px solid #444;
                padding: 6px;
                border-radius: 6px;
            }
            QTableWidget {
                background-color: #1a1a1a;
                color: #e5e5e5;
                gridline-color: #3e3e50;
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #212121;
                color: #e5e5e5;
                padding: 6px;
                border: 1px solid #444;
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #a0a0a0;
            }
        """)

    def simpan_kegiatan(self):
        judul = self.input_judul.text()
        lokasi = self.input_lokasi.text()
        status = self.input_status.currentText()
        catatan = self.input_catatan.toPlainText()

        if not judul or not self.input_tanggal.date().isValid():
            QMessageBox.warning(self, "Peringatan", "Judul dan Tanggal tidak boleh kosong.")
            return

        tanggal = self.input_tanggal.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO kegiatan (judul, lokasi, tanggal, status, catatan) VALUES (?, ?, ?, ?, ?)",
                       (judul, lokasi, tanggal, status, catatan))
        conn.commit()
        conn.close()
        self.load_data()
        self.clear_form()

    def barisklik(self, row):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, judul, lokasi, tanggal, status, catatan FROM kegiatan")
        data = cursor.fetchall()
        if row < len(data):
            selected = data[row]
            self.selected_row_id = selected[0]
            self.input_judul.setText(selected[1])
            self.input_lokasi.setText(selected[2])
            self.input_tanggal.setDate(QDate.fromString(selected[3]))
            index = self.input_status.findText(selected[4])
            if index != -1:
                self.input_status.setCurrentIndex(index)
            self.input_catatan.setText(selected[5])
        conn.close()

    def update_kegiatan(self):
        if self.selected_row_id is None:
            QMessageBox.warning(self, "Peringatan", "Pilih baris terlebih dahulu.")
            return

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE kegiatan 
            SET judul = ?, lokasi = ?, tanggal = ?, status = ?, catatan = ?
            WHERE id = ?
        ''', (
            self.input_judul.text(),
            self.input_lokasi.text(),
            self.input_tanggal.date().toString("yyyy-MM-dd"),
            self.input_status.currentText(), 
            self.input_catatan.toPlainText(),
            self.selected_row_id
        ))
        conn.commit()
        conn.close()
        self.load_data()
        self.clear_form()


    def hapus_kegiatan(self):
        if self.selected_row_id is None:
            QMessageBox.warning(self, "Peringatan", "Pilih baris terlebih dahulu.")
            return

        confirm = QMessageBox.question(self, "Hapus", "Yakin ingin menghapus kegiatan ini?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kegiatan WHERE id = ?", (self.selected_row_id,))
            conn.commit()
            conn.close()
            self.load_data()
            self.clear_form()

    def load_data(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, judul, lokasi, tanggal, status, catatan FROM kegiatan")
        for row_number, row_data in enumerate(cursor.fetchall()):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data[1:]): 
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        conn.close()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if path:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT judul, lokasi, tanggal, status, catatan FROM kegiatan")
            data = cursor.fetchall()
            conn.close()
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Judul", "Lokasi", "Tanggal", "Status", "Catatan"])
                writer.writerows(data)
            QMessageBox.information(self, "Berhasil", "Data berhasil diexport ke CSV.")


    def export_pdf(self):
        from fpdf import FPDF

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT judul, lokasi, tanggal, status, catatan FROM kegiatan")
        data = cursor.fetchall()
        conn.close()

        if not data:
            QMessageBox.warning(self, "Kosong", "Tidak ada data untuk diexport.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Daftar Kegiatan - KegiatanKu", ln=True, align='C')
        pdf.set_font("Arial", 'B', 10)
        pdf.ln(5)
        pdf.cell(40, 10, "Judul", 1)
        pdf.cell(35, 10, "Lokasi", 1)
        pdf.cell(30, 10, "Tanggal", 1)
        pdf.cell(35, 10, "Status", 1)
        pdf.cell(50, 10, "Catatan", 1)
        pdf.ln()

        pdf.set_font("Arial", '', 10)
        for row in data:
            pdf.cell(40, 10, str(row[0])[:20], 1)
            pdf.cell(35, 10, str(row[1])[:20], 1)
            pdf.cell(30, 10, str(row[2]), 1)
            pdf.cell(35, 10, str(row[3])[:20], 1)
            pdf.cell(50, 10, str(row[4])[:30], 1)
            pdf.ln()

        path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", "", "PDF Files (*.pdf)")
        if path:
            pdf.output(path)
            QMessageBox.information(self, "Berhasil", "Data berhasil diexport ke PDF.")

    def clear_form(self):
        self.input_judul.clear()
        self.input_lokasi.clear()
        self.input_tanggal.setDate(QDate())  
        self.input_status.setCurrentIndex(0)
        self.input_catatan.clear()
        self.selected_row_id = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KegiatanKu()
    window.show()
    sys.exit(app.exec_())
