# /****************************************************
#  * MSSV: 202418913
#  * Họ và tên: Nguyễn Đức Hưng
#  ****************************************************/

"""Bảng lương của một kỳ. Payroll CHỨA các Employee (quan hệ tập hợp
1 Payroll -> 0..* Employee), không kế thừa Employee.

Mọi phép tổng hợp chỉ gọi calculateGrossPay() qua kiểu chung Employee
(đa hình), không có if/else theo loại nhân sự.
"""
import re

from models import Employee, formatMoney, _requireText


class Payroll:
    _PERIOD_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

    def __init__(self, period):
        self.period = period
        self._employees = []  # lưu THAM CHIẾU tới đối tượng Employee

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        if not isinstance(value, str) or not self._PERIOD_PATTERN.match(value.strip()):
            raise ValueError("Kỳ lương phải có dạng YYYY-MM, ví dụ 2026-09")
        self._period = value.strip()

    @property
    def employees(self):
        return tuple(self._employees)

    def __len__(self):
        return len(self._employees)

    def addEmployee(self, employee):
        if not isinstance(employee, Employee):
            raise TypeError("Chỉ được thêm đối tượng Employee")
        if self.findEmployee(employee.employeeId) is not None:
            raise ValueError(f"Mã nhân sự {employee.employeeId} đã tồn tại trong bảng lương")
        self._employees.append(employee)

    def findEmployee(self, employeeId):
        """Trả về Employee hoặc None nếu không tìm thấy."""
        key = employeeId.strip() if isinstance(employeeId, str) else employeeId
        for employee in self._employees:
            if employee.employeeId == key:
                return employee
        return None

    def calculateTotalPayroll(self):
        return sum(e.calculateGrossPay() for e in self._employees)

    def calculatePayrollByDepartment(self, department):
        key = _requireText(department, "Phòng ban không được rỗng").casefold()
        return sum(e.calculateGrossPay() for e in self._employees
                   if e.department.casefold() == key)

    def findHighestPaidEmployee(self):
        """Trả về None nếu bảng lương rỗng."""
        if not self._employees:
            return None
        return max(self._employees, key=lambda e: e.calculateGrossPay())

    def startNewPeriod(self, period):
        """Chuyển sang kỳ mới: đổi kỳ lương và đặt lại dữ liệu theo kỳ của mọi
        nhân sự (thưởng, số giờ, doanh số) - lời gọi đa hình."""
        self.period = period
        for employee in self._employees:
            employee.resetForNewPeriod()

    def displayPayroll(self):
        print(f"===== BẢNG LƯƠNG KỲ {self.period} =====")
        if not self._employees:
            print("(Bảng lương rỗng)")
            return
        for employee in self._employees:
            employee.displayPayrollInfo()  # lời gọi đa hình
            print("-" * 50)
        print(f"TỔNG BẢNG LƯƠNG: {formatMoney(self.calculateTotalPayroll())}")
        top = self.findHighestPaidEmployee()
        print(f"Thu nhập cao nhất: {top.fullName} ({formatMoney(top.calculateGrossPay())})")
