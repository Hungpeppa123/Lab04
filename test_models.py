# /****************************************************
#  * MSSV: 202418913
#  * Họ và tên: Nguyễn Đức Hưng
#  ****************************************************/

"""Kiểm thử đơn vị (phần C và C.1). Chạy: python -m unittest -v"""
import unittest

from models import Employee, SalariedEmployee, HourlyEmployee, SalesEmployee
from payroll import Payroll
from main import buildSamplePayroll


class SampleDataTest(unittest.TestCase):
    """Dữ liệu kiểm thử phần C."""

    def setUp(self):
        self.payroll = buildSamplePayroll()

    def test_salaried_E001(self):
        self.assertAlmostEqual(self.payroll.findEmployee("E001").calculateGrossPay(), 18_000_000)

    def test_hourly_no_overtime_E002(self):
        self.assertAlmostEqual(self.payroll.findEmployee("E002").calculateGrossPay(), 15_500_000)

    def test_hourly_overtime_E003(self):
        chi = self.payroll.findEmployee("E003")
        self.assertEqual(chi.overtimeHours, 10)
        self.assertAlmostEqual(chi.calculateGrossPay(), 17_500_000)

    def test_sales_E004(self):
        self.assertAlmostEqual(self.payroll.findEmployee("E004").calculateGrossPay(), 19_000_000)

    def test_total_and_department(self):
        self.assertAlmostEqual(self.payroll.calculateTotalPayroll(), 70_000_000)
        self.assertAlmostEqual(self.payroll.calculatePayrollByDepartment("Hỗ trợ"), 33_000_000)

    def test_highest_paid(self):
        self.assertEqual(self.payroll.findHighestPaidEmployee().employeeId, "E004")


class BoundaryAndErrorTest(unittest.TestCase):
    """Kiểm thử biên và kiểm thử lỗi (C.1)."""

    # --- Employee / constructor ---
    def test_01_empty_id_name_department(self):
        with self.assertRaises(ValueError):
            SalariedEmployee("", "A", 1)
        with self.assertRaises(ValueError):
            SalariedEmployee("E1", "   ", 1)
        with self.assertRaises(ValueError):
            SalariedEmployee("E1", "A", "", 1, 0)

    def test_02_short_constructor_defaults(self):
        e = SalariedEmployee("E1", "A", 10_000_000)
        self.assertEqual(e.department, "Unassigned")
        self.assertEqual(e.monthlyBonus, 0)
        self.assertEqual(e.responsibilityAllowance, 0)
        self.assertEqual(HourlyEmployee("E2", "B", 50_000).workedHours, 0)
        sales = SalesEmployee("E3", "C", 5_000_000)
        self.assertEqual(sales.salesRevenue, 0)
        self.assertEqual(sales.commissionRate, SalesEmployee.DEFAULT_COMMISSION_RATE)

    def test_03_wrong_argument_count(self):
        with self.assertRaises(TypeError):
            SalariedEmployee("E1", "A", "Phòng", 1)
        with self.assertRaises(TypeError):
            SalariedEmployee("E1", "A", 1).addBonus()

    def test_04_employee_is_abstract(self):
        with self.assertRaises(TypeError):
            Employee("E1", "A")

    def test_05_negative_salary_allowance(self):
        with self.assertRaises(ValueError):
            SalariedEmployee("E1", "A", -1)
        with self.assertRaises(ValueError):
            SalariedEmployee("E1", "A", "P", 1, -1)

    # --- HourlyEmployee ---
    def test_06_worked_hours_boundaries(self):
        HourlyEmployee("E1", "A", "P", 100_000, 0)
        e = HourlyEmployee("E2", "B", "P", 100_000, 250)
        self.assertAlmostEqual(e.calculateGrossPay(), 160 * 100_000 + 90 * 100_000 * 1.5)
        e160 = HourlyEmployee("E3", "C", "P", 100_000, 160)
        self.assertEqual(e160.overtimeHours, 0)
        for bad in (-1, 250.5, 251):
            with self.assertRaises(ValueError):
                HourlyEmployee("E4", "D", "P", 100_000, bad)

    def test_07_hourly_rate_must_be_positive(self):
        with self.assertRaises(ValueError):
            HourlyEmployee("E1", "A", 0)

    # --- SalesEmployee ---
    def test_08_commission_rate_boundaries(self):
        SalesEmployee("E1", "A", "P", 1, 1, 0)
        SalesEmployee("E2", "B", "P", 1, 1, 0.3)
        for bad in (-0.01, 0.31):
            with self.assertRaises(ValueError):
                SalesEmployee("E3", "C", "P", 1, 1, bad)

    def test_09_controlled_sales_update(self):
        e = SalesEmployee("E1", "A", "P", 1_000, 0, 0.1)
        e.recordSale(10_000)
        e.updateSalesRevenue(20_000)
        self.assertEqual(e.salesRevenue, 20_000)
        with self.assertRaises(ValueError):
            e.updateSalesRevenue(-1)
        with self.assertRaises(ValueError):
            e.recordSale(0)
        with self.assertRaises(AttributeError):
            e.salesRevenue = 5  # không có setter trực tiếp

    # --- addBonus ---
    def test_10_bonus_amount_must_be_positive(self):
        e = SalariedEmployee("E1", "A", 1)
        for bad in (0, -100):
            with self.assertRaises(ValueError):
                e.addBonus(bad)
        with self.assertRaises(TypeError):
            e.addBonus("100")
        self.assertEqual(e.monthlyBonus, 0)  # lỗi không làm đổi trạng thái

    def test_11_bonus_rate_boundaries(self):
        e = SalariedEmployee("E1", "A", 1)
        e.addBonus(0.5, 1_000, "Tối đa")
        self.assertAlmostEqual(e.monthlyBonus, 500)
        for bad in (0, 0.51):
            with self.assertRaises(ValueError):
                e.addBonus(bad, 1_000, "x")
        with self.assertRaises(ValueError):
            e.addBonus(0.1, 0, "x")

    def test_12_bonus_reason_not_empty(self):
        e = SalariedEmployee("E1", "A", 1)
        with self.assertRaises(ValueError):
            e.addBonus(100, "  ")
        with self.assertRaises(ValueError):
            e.addBonus(0.1, 1_000, "")
        with self.assertRaises(TypeError):
            e.addBonus(0.02, 50_000_000)  # thưởng theo tỷ lệ nhưng quên lý do
        self.assertEqual(e.monthlyBonus, 0)

    def test_13_bonus_history_and_reset(self):
        e = SalariedEmployee("E1", "A", 1)
        e.addBonus(100)
        e.addBonus(200, "Lý do")
        e.addBonus(0.1, 1_000, "Tỷ lệ")
        self.assertEqual(len(e.bonusHistory), 3)
        self.assertAlmostEqual(e.monthlyBonus, 400)
        e.resetBonus()
        self.assertEqual(e.monthlyBonus, 0)

    # --- Payroll ---
    def test_14_duplicate_id_rejected(self):
        p = Payroll("2026-09")
        p.addEmployee(SalariedEmployee("E1", "A", 1))
        with self.assertRaises(ValueError):
            p.addEmployee(HourlyEmployee("E1", "B", 1))
        self.assertEqual(len(p), 1)

    def test_15_empty_payroll(self):
        p = Payroll("2026-09")
        self.assertEqual(p.calculateTotalPayroll(), 0)
        self.assertEqual(p.calculatePayrollByDepartment("Hỗ trợ"), 0)
        self.assertIsNone(p.findHighestPaidEmployee())
        self.assertIsNone(p.findEmployee("E1"))

    def test_16_invalid_period_and_non_employee(self):
        with self.assertRaises(ValueError):
            Payroll("2026-13")
        with self.assertRaises(TypeError):
            Payroll("2026-09").addEmployee("E1")

    def test_17_payroll_keeps_reference(self):
        p = Payroll("2026-09")
        e = SalariedEmployee("E1", "A", 1_000)
        p.addEmployee(e)
        e.addBonus(500)  # thay đổi bên ngoài phản ánh vào bảng lương
        self.assertEqual(p.calculateTotalPayroll(), 1_500)

    def test_18_start_new_period_resets_period_data(self):
        p = buildSamplePayroll()
        p.startNewPeriod("2026-10")
        self.assertEqual(p.period, "2026-10")
        self.assertTrue(all(e.monthlyBonus == 0 for e in p.employees))
        self.assertEqual(p.findEmployee("E003").workedHours, 0)
        self.assertEqual(p.findEmployee("E004").salesRevenue, 0)
        # Chỉ còn phần cố định: 15tr + 2tr (E001) và 8tr (E004)
        self.assertAlmostEqual(p.calculateTotalPayroll(), 25_000_000)

    def test_19_department_query_rejects_none(self):
        with self.assertRaises(ValueError):
            buildSamplePayroll().calculatePayrollByDepartment(None)

    def test_20_non_finite_numbers_rejected(self):
        e = SalariedEmployee("E1", "A", 1)
        for bad in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                e.addBonus(bad)
        self.assertEqual(e.monthlyBonus, 0)

    def test_21_employee_id_read_only(self):
        e = SalariedEmployee("E1", "A", 1)
        with self.assertRaises(AttributeError):
            e.employeeId = "E2"

    # --- Bổ sung trường hợp biên ---
    def test_22_numeric_edge_values(self):
        self.assertEqual(SalariedEmployee("E1", "A", 0).calculateGrossPay(), 0)  # lương 0 hợp lệ
        self.assertEqual(HourlyEmployee("E2", "B", "P", 100, 160.5).overtimeHours, 0.5)
        with self.assertRaises(ValueError):
            HourlyEmployee("E3", "C", -1)
        with self.assertRaises(TypeError):
            SalariedEmployee("E4", "D", True)  # bool không được coi là số
        e = SalariedEmployee("E5", "E", 1)
        self.assertEqual(e.addBonus(0.01), 0.01)  # số dương nhỏ nhất vẫn hợp lệ
        with self.assertRaises(ValueError):
            e.addBonus(0.1, -1, "x")
        with self.assertRaises(TypeError):
            e.addBonus(0.1, 1_000, "x", "thừa")
        with self.assertRaises(ValueError):
            e.addBonus(0.1, 1_000, None)

    def test_23_period_boundaries(self):
        for ok in ("2026-01", "2026-12", " 2026-09 "):
            Payroll(ok)
        for bad in ("2026-00", "2026-1", "26-09", "", None):
            with self.assertRaises(ValueError):
                Payroll(bad)

    def test_24_lookup_normalization(self):
        p = buildSamplePayroll()
        self.assertEqual(p.findEmployee(" E001 ").employeeId, "E001")
        self.assertIsNone(p.findEmployee(None))
        with self.assertRaises(ValueError):
            p.addEmployee(SalariedEmployee(" E001 ", "Trùng", 1))  # mã được strip
        self.assertAlmostEqual(p.calculatePayrollByDepartment("  hỗ TRỢ "), 33_000_000)
        self.assertEqual(p.calculatePayrollByDepartment("Không tồn tại"), 0)

    def test_25_invalid_new_period_keeps_data(self):
        p = buildSamplePayroll()
        with self.assertRaises(ValueError):
            p.startNewPeriod("2026-13")
        self.assertEqual(p.period, "2026-09")
        self.assertAlmostEqual(p.calculateTotalPayroll(), 70_000_000)  # chưa bị đặt lại
        empty = Payroll("2026-09")
        empty.startNewPeriod("2026-10")
        self.assertEqual(empty.period, "2026-10")

    def test_26_highest_paid_tie_returns_first(self):
        p = Payroll("2026-09")
        p.addEmployee(SalariedEmployee("E1", "A", 1_000))
        p.addEmployee(SalariedEmployee("E2", "B", 1_000))
        self.assertEqual(p.findHighestPaidEmployee().employeeId, "E1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
