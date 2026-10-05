# /****************************************************
#  * MSSV: 202418913
#  * Họ và tên: Nguyễn Đức Hưng
#  ****************************************************/

"""Chạy dữ liệu kiểm thử phần C và minh họa các tình huống lỗi."""
import sys

from models import (Employee, SalariedEmployee, HourlyEmployee, SalesEmployee,
                    formatMoney)
from payroll import Payroll


def buildSamplePayroll():
    payroll = Payroll("2026-09")

    an = SalariedEmployee("E001", "Nguyễn Minh An", "Đào tạo", 15_000_000, 2_000_000)
    an.addBonus(1_000_000)                                     # addBonus(amount)

    binh = HourlyEmployee("E002", "Trần Thu Bình", "Hỗ trợ", 100_000, 150)
    binh.addBonus(500_000, "Hỗ trợ khách hàng xuất sắc")       # addBonus(amount, reason)

    chi = HourlyEmployee("E003", "Lê Hoàng Chi", "Hỗ trợ", 100_000, 170)

    dung = SalesEmployee("E004", "Phạm Quốc Dũng", "Kinh doanh",
                         8_000_000, 200_000_000, 0.05)
    dung.addBonus(0.02, 50_000_000, "Vượt chỉ tiêu dự án")     # addBonus(rate, ref, reason)

    for employee in (an, binh, chi, dung):
        payroll.addEmployee(employee)
    return payroll


def demoErrors(payroll):
    print("\n===== TÌNH HUỐNG LỖI =====")
    cases = [
        ("Mã rỗng", lambda: SalariedEmployee("  ", "A", 1)),
        ("Số giờ 251", lambda: HourlyEmployee("X1", "B", "Hỗ trợ", 100_000, 251)),
        ("Hoa hồng 0,31", lambda: SalesEmployee("X2", "C", "KD", 1, 1, 0.31)),
        ("Thưởng 0", lambda: payroll.findEmployee("E001").addBonus(0)),
        ("Tỷ lệ thưởng 0,6", lambda: payroll.findEmployee("E001").addBonus(0.6, 1_000, "x")),
        ("Lý do rỗng", lambda: payroll.findEmployee("E001").addBonus(100, "   ")),
        ("Trùng mã E001", lambda: payroll.addEmployee(SalariedEmployee("E001", "D", 1))),
        ("Khởi tạo Employee trừu tượng", lambda: Employee("E9", "E")),
    ]
    for name, action in cases:
        try:
            action()
            print(f"{name}: KHÔNG phát sinh lỗi (!)")
        except (ValueError, TypeError) as error:
            print(f"{name}: {type(error).__name__} - {error}")

    demoBoundaries(payroll)

    empty = Payroll("2026-10")
    print("\nBảng lương rỗng -> tổng =", empty.calculateTotalPayroll(),
          "| cao nhất =", empty.findHighestPaidEmployee())
    empty.displayPayroll()


def demoBoundaries(payroll):
    print("\n===== TRƯỜNG HỢP BIÊN =====")
    print("Đúng 160 giờ   -> giờ vượt ngưỡng =",
          HourlyEmployee("B1", "A", "P", 100_000, 160).overtimeHours)
    print("160,5 giờ      -> giờ vượt ngưỡng =",
          HourlyEmployee("B2", "B", "P", 100_000, 160.5).overtimeHours)
    print("250 giờ (max)  -> gross =",
          formatMoney(HourlyEmployee("B3", "C", "P", 100_000, 250).calculateGrossPay()))
    print("Hoa hồng 0,3   -> hợp lệ:", SalesEmployee("B4", "D", "P", 1, 1, 0.3).commissionRate)
    bonus = SalariedEmployee("B5", "E", 1).addBonus(0.5, 1_000_000, "Tỷ lệ tối đa")
    print("Tỷ lệ thưởng 0,5 -> thưởng =", formatMoney(bonus))
    print("Tìm ' E001 '   ->", payroll.findEmployee(" E001 ").fullName)
    print("Phòng ' hỗ TRỢ ' ->", formatMoney(payroll.calculatePayrollByDepartment(" hỗ TRỢ ")))
    cases = [
        ("Số giờ 250,5", lambda: HourlyEmployee("X1", "A", "P", 100_000, 250.5)),
        ("Tỷ lệ thưởng 0,51", lambda: payroll.findEmployee("E001").addBonus(0.51, 1_000, "x")),
        ("Thưởng NaN", lambda: payroll.findEmployee("E001").addBonus(float("nan"))),
        ("Thưởng tỷ lệ thiếu lý do", lambda: payroll.findEmployee("E001").addBonus(0.02, 50_000_000)),
        ("Lương = True", lambda: SalariedEmployee("X2", "B", True)),
        ("Kỳ lương 2026-00", lambda: Payroll("2026-00")),
        ("Phòng ban None", lambda: payroll.calculatePayrollByDepartment(None)),
    ]
    for name, action in cases:
        try:
            action()
            print(f"{name}: KHÔNG phát sinh lỗi (!)")
        except (ValueError, TypeError) as error:
            print(f"{name}: {type(error).__name__} - {error}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    payroll = buildSamplePayroll()
    payroll.displayPayroll()
    demoErrors(payroll)
