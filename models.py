# /****************************************************
#  * MSSV: 202418913
#  * Họ và tên: Nguyễn Đức Hưng
#  ****************************************************/

"""Mô hình nhân sự cho hệ thống tính lương (Lab 04: Overloading & Overriding).

Python không hỗ trợ nạp chồng như C++/Java, nên:
- Nạp chồng constructor được mô phỏng bằng *args + kiểm tra số lượng tham số.
  Lớp dẫn xuất ủy quyền phần chung cho super().__init__(), và mọi kiểm tra
  dữ liệu nằm trong setter của property -> không lặp lại logic kiểm tra.
- Nạp chồng addBonus() được mô phỏng bằng *args, phân nhánh theo số tham số
  rồi chuyển về một phương thức nội bộ duy nhất _recordBonus().
- Ghi đè (overriding) dùng cơ chế tự nhiên của Python; Employee là lớp
  trừu tượng (ABC) với các phương thức @abstractmethod.
"""
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from numbers import Real
from typing import Optional


# ----- Hàm tiện ích kiểm tra dữ liệu (dùng chung, tránh lặp) -----
def _requireText(value, message):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(message)
    return value.strip()


def _requireNumber(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} phải là số")
    if not math.isfinite(value):
        raise ValueError(f"{name} phải là số hữu hạn")
    return value


def _requireNonNegative(value, name):
    _requireNumber(value, name)
    if value < 0:
        raise ValueError(f"{name} không được âm")
    return value


def _requirePositive(value, name):
    _requireNumber(value, name)
    if value <= 0:
        raise ValueError(f"{name} phải lớn hơn 0")
    return value


def formatMoney(amount):
    """15000000 -> '15.000.000'"""
    return f"{amount:,.0f}".replace(",", ".")


@dataclass(frozen=True)
class BonusRecord:
    """Một khoản thưởng đã ghi nhận. Bất biến sau khi tạo.

    Lưu lịch sử bằng danh sách các đối tượng BonusRecord (không dùng mảng song
    song amount[] / reason[]), để kế toán đối soát được từng khoản thưởng.
    """
    amount: float
    reason: Optional[str] = None
    rate: Optional[float] = None
    referenceAmount: Optional[float] = None

    def describe(self):
        text = formatMoney(self.amount)
        if self.rate is not None:
            text += f" ({self.rate:.0%} x {formatMoney(self.referenceAmount)})"
        if self.reason:
            text += f" - {self.reason}"
        return text


class Employee(ABC):
    """Lớp cơ sở trừu tượng cho mọi loại nhân sự."""
    DEFAULT_DEPARTMENT = "Unassigned"
    MAX_BONUS_RATE = 0.5

    def __init__(self, *args):
        # Employee(employeeId, fullName)
        # Employee(employeeId, fullName, department)
        if len(args) == 2:
            employeeId, fullName = args
            department = self.DEFAULT_DEPARTMENT
        elif len(args) == 3:
            employeeId, fullName, department = args
        else:
            raise TypeError("Employee nhận 2 hoặc 3 tham số")
        # Mã nhân sự chỉ gán một lần (không có setter) -> tránh trùng mã
        self._employeeId = _requireText(employeeId, "Mã nhân sự không được rỗng")
        # Gán qua property -> setter tự kiểm tra bất biến
        self.fullName = fullName
        self.department = department
        self._bonusHistory = []  # monthlyBonus = 0

    # ----- Property -----
    @property
    def employeeId(self):
        return self._employeeId

    @property
    def fullName(self):
        return self._fullName

    @fullName.setter
    def fullName(self, value):
        self._fullName = _requireText(value, "Họ tên không được rỗng")

    @property
    def department(self):
        return self._department

    @department.setter
    def department(self, value):
        self._department = _requireText(value, "Phòng ban không được rỗng")

    @property
    def monthlyBonus(self):
        """Tổng thưởng trong tháng, suy ra từ lịch sử (chỉ đọc).

        Mỗi khoản thưởng luôn > 0 nên tổng không bao giờ âm.
        """
        return sum(record.amount for record in self._bonusHistory)

    @property
    def bonusHistory(self):
        return tuple(self._bonusHistory)  # bản sao chỉ đọc

    # ----- Nạp chồng addBonus() -----
    def addBonus(self, *args):
        # addBonus(amount)
        # addBonus(amount, reason)
        # addBonus(rate, referenceAmount, reason)
        if len(args) == 1:
            return self._addFixedBonus(args[0], None)
        if len(args) == 2:
            if isinstance(args[1], Real) and not isinstance(args[1], bool):
                # addBonus(rate, referenceAmount) -> quên lý do
                raise TypeError("Thưởng theo tỷ lệ cần lý do: "
                                "addBonus(rate, referenceAmount, reason)")
            return self._addFixedBonus(args[0], args[1])
        if len(args) == 3:
            return self._addRateBonus(*args)
        raise TypeError("addBonus nhận 1, 2 hoặc 3 tham số")

    def _addFixedBonus(self, amount, reason):
        _requirePositive(amount, "Khoản thưởng")
        return self._recordBonus(BonusRecord(amount, self._checkReason(reason)))

    def _addRateBonus(self, rate, referenceAmount, reason):
        _requireNumber(rate, "Tỷ lệ thưởng")
        if not 0 < rate <= self.MAX_BONUS_RATE:
            raise ValueError("Tỷ lệ thưởng phải trong (0; 0,5]")
        _requirePositive(referenceAmount, "Giá trị tham chiếu")
        reason = _requireText(reason, "Lý do thưởng không được rỗng")
        return self._recordBonus(
            BonusRecord(rate * referenceAmount, reason, rate, referenceAmount))

    @staticmethod
    def _checkReason(reason):
        if reason is None:
            return None
        return _requireText(reason, "Lý do thưởng không được rỗng")

    def _recordBonus(self, record):
        self._bonusHistory.append(record)
        return record.amount

    def resetBonus(self):
        """Đặt lại thưởng khi bắt đầu kỳ lương mới."""
        self._bonusHistory.clear()

    def resetForNewPeriod(self):
        """Đặt lại dữ liệu theo kỳ. Lớp dẫn xuất ghi đè để đặt lại phần riêng."""
        self.resetBonus()

    # ----- Phương thức cần ghi đè -----
    @abstractmethod
    def calculateGrossPay(self):
        """Thu nhập trước khấu trừ - mỗi lớp dẫn xuất có công thức riêng."""

    @abstractmethod
    def getEmployeeType(self):
        """Tên loại nhân sự."""

    def displayPayrollInfo(self):
        """Khung hiển thị chung; phần riêng do _displayPayComponents() đảm nhận."""
        print(f"[{self.getEmployeeType()}] {self.employeeId} - {self.fullName}"
              f" | Phòng: {self.department}")
        self._displayPayComponents()
        print(f"   Thưởng            : {formatMoney(self.monthlyBonus)}")
        for record in self._bonusHistory:
            print(f"     + {record.describe()}")
        print(f"   => Thu nhập (gross): {formatMoney(self.calculateGrossPay())}")

    @abstractmethod
    def _displayPayComponents(self):
        """In các thành phần lương riêng của từng loại nhân sự."""

    def __str__(self):
        return (f"{self.getEmployeeType()}({self.employeeId}, {self.fullName}, "
                f"{formatMoney(self.calculateGrossPay())})")


class SalariedEmployee(Employee):
    """Nhân viên hưởng lương cố định."""

    def __init__(self, *args):
        # Rút gọn: SalariedEmployee(employeeId, fullName, monthlySalary)
        # Đầy đủ : SalariedEmployee(employeeId, fullName, department,
        #                           monthlySalary, responsibilityAllowance)
        if len(args) == 3:
            employeeId, fullName, monthlySalary = args
            super().__init__(employeeId, fullName)
            allowance = 0
        elif len(args) == 5:
            employeeId, fullName, department, monthlySalary, allowance = args
            super().__init__(employeeId, fullName, department)
        else:
            raise TypeError("SalariedEmployee nhận 3 hoặc 5 tham số")
        self.monthlySalary = monthlySalary
        self.responsibilityAllowance = allowance

    @property
    def monthlySalary(self):
        return self._monthlySalary

    @monthlySalary.setter
    def monthlySalary(self, value):
        self._monthlySalary = _requireNonNegative(value, "Lương tháng")

    @property
    def responsibilityAllowance(self):
        return self._responsibilityAllowance

    @responsibilityAllowance.setter
    def responsibilityAllowance(self, value):
        self._responsibilityAllowance = _requireNonNegative(value, "Phụ cấp trách nhiệm")

    def calculateGrossPay(self):
        return self.monthlySalary + self.responsibilityAllowance + self.monthlyBonus

    def getEmployeeType(self):
        return "Lương cố định"

    def _displayPayComponents(self):
        print(f"   Lương tháng       : {formatMoney(self.monthlySalary)}")
        print(f"   Phụ cấp trách nhiệm: {formatMoney(self.responsibilityAllowance)}")


class HourlyEmployee(Employee):
    """Nhân viên hưởng lương theo giờ."""
    REGULAR_HOURS_LIMIT = 160
    OVERTIME_MULTIPLIER = 1.5
    MAX_WORKED_HOURS = 250

    def __init__(self, *args):
        # Rút gọn: HourlyEmployee(employeeId, fullName, hourlyRate)  -> 0 giờ
        # Đầy đủ : HourlyEmployee(employeeId, fullName, department,
        #                         hourlyRate, workedHours)
        if len(args) == 3:
            employeeId, fullName, hourlyRate = args
            super().__init__(employeeId, fullName)
            workedHours = 0
        elif len(args) == 5:
            employeeId, fullName, department, hourlyRate, workedHours = args
            super().__init__(employeeId, fullName, department)
        else:
            raise TypeError("HourlyEmployee nhận 3 hoặc 5 tham số")
        self.hourlyRate = hourlyRate
        self.workedHours = workedHours

    @property
    def hourlyRate(self):
        return self._hourlyRate

    @hourlyRate.setter
    def hourlyRate(self, value):
        self._hourlyRate = _requirePositive(value, "Đơn giá giờ")

    @property
    def workedHours(self):
        return self._workedHours

    @workedHours.setter
    def workedHours(self, value):
        _requireNumber(value, "Số giờ làm")
        if not 0 <= value <= self.MAX_WORKED_HOURS:
            raise ValueError(f"Số giờ làm phải trong [0; {self.MAX_WORKED_HOURS}]")
        self._workedHours = value

    # Các giá trị suy ra từ trạng thái -> không lưu riêng
    @property
    def regularHours(self):
        return min(self.workedHours, self.REGULAR_HOURS_LIMIT)

    @property
    def overtimeHours(self):
        return max(0, self.workedHours - self.REGULAR_HOURS_LIMIT)

    @property
    def regularPay(self):
        return self.regularHours * self.hourlyRate

    @property
    def overtimePay(self):
        return self.overtimeHours * self.hourlyRate * self.OVERTIME_MULTIPLIER

    @property
    def basePay(self):
        return self.regularPay + self.overtimePay

    def calculateGrossPay(self):
        return self.basePay + self.monthlyBonus

    def getEmployeeType(self):
        return "Theo giờ"

    def resetForNewPeriod(self):
        super().resetForNewPeriod()
        self.workedHours = 0  # chấm công lại từ đầu

    def _displayPayComponents(self):
        print(f"   Đơn giá giờ       : {formatMoney(self.hourlyRate)}")
        print(f"   Giờ thường        : {self.regularHours} -> {formatMoney(self.regularPay)}")
        print(f"   Giờ vượt ngưỡng   : {self.overtimeHours} x{self.OVERTIME_MULTIPLIER}"
              f" -> {formatMoney(self.overtimePay)}")


class SalesEmployee(Employee):
    """Nhân viên kinh doanh: lương cơ bản + hoa hồng."""
    MAX_COMMISSION_RATE = 0.3
    DEFAULT_COMMISSION_RATE = 0.05

    def __init__(self, *args):
        # Rút gọn: SalesEmployee(employeeId, fullName, baseSalary)
        #          -> doanh số 0, hoa hồng theo DEFAULT_COMMISSION_RATE
        # Đầy đủ : SalesEmployee(employeeId, fullName, department,
        #                        baseSalary, salesRevenue, commissionRate)
        if len(args) == 3:
            employeeId, fullName, baseSalary = args
            super().__init__(employeeId, fullName)
            salesRevenue, commissionRate = 0, self.DEFAULT_COMMISSION_RATE
        elif len(args) == 6:
            (employeeId, fullName, department,
             baseSalary, salesRevenue, commissionRate) = args
            super().__init__(employeeId, fullName, department)
        else:
            raise TypeError("SalesEmployee nhận 3 hoặc 6 tham số")
        self.baseSalary = baseSalary
        self.updateSalesRevenue(salesRevenue)
        self.commissionRate = commissionRate

    @property
    def baseSalary(self):
        return self._baseSalary

    @baseSalary.setter
    def baseSalary(self, value):
        self._baseSalary = _requireNonNegative(value, "Lương cơ bản")

    @property
    def salesRevenue(self):
        # Chỉ đọc: cập nhật qua updateSalesRevenue() / recordSale()
        return self._salesRevenue

    def updateSalesRevenue(self, newRevenue):
        """Cập nhật doanh số có kiểm soát (không âm)."""
        self._salesRevenue = _requireNonNegative(newRevenue, "Doanh số")

    def recordSale(self, amount):
        """Cộng thêm một giao dịch bán hàng (phải > 0)."""
        self._salesRevenue += _requirePositive(amount, "Giá trị giao dịch")

    @property
    def commissionRate(self):
        return self._commissionRate

    @commissionRate.setter
    def commissionRate(self, value):
        _requireNumber(value, "Tỷ lệ hoa hồng")
        if not 0 <= value <= self.MAX_COMMISSION_RATE:
            raise ValueError("Tỷ lệ hoa hồng phải trong [0; 0,3]")
        self._commissionRate = value

    @property
    def commission(self):
        return self.salesRevenue * self.commissionRate

    def calculateGrossPay(self):
        return self.baseSalary + self.commission + self.monthlyBonus

    def getEmployeeType(self):
        return "Kinh doanh"

    def resetForNewPeriod(self):
        super().resetForNewPeriod()
        self.updateSalesRevenue(0)  # doanh số tính lại theo kỳ

    def _displayPayComponents(self):
        print(f"   Lương cơ bản      : {formatMoney(self.baseSalary)}")
        print(f"   Hoa hồng          : {formatMoney(self.salesRevenue)} x"
              f" {self.commissionRate:.0%} = {formatMoney(self.commission)}")
