# Copyright 2017 Comunitea Servicios Tecnológicos S.L.
# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class HrEmployeeBase(models.AbstractModel):

    _inherit = "hr.employee.base"
    _sql_constraints = [
        (
            "rfid_card_code_uniq",
            "UNIQUE(rfid_card_code)",
            "The rfid code should be unique.",
        )
    ]

    rfid_card_code = fields.Char("RFID Card Code", copy=False)

    @api.model
    def register_attendance(self, card_code):
        """Register the attendance of the employee.
        :returns: dictionary
            'rfid_card_code': char
            'employee_name': char
            'employee_id': int
            'error_message': char
            'logged': boolean
            'action': check_in/check_out
        """

        res = {
            "rfid_card_code": card_code,
            "employee_name": "",
            "employee_id": False,
            "error_message": "",
            "logged": False,
            "action": "FALSE",
        }
        # We need to apply sudo() because a RFID basic user does not have access to
        # hr.employee. Hr.employee.public model does not have the
        # _attendance_action_change() method that will be used later.
        employee = self.sudo().search([("rfid_card_code", "=", card_code)], limit=1)
        if employee:
            res["employee_name"] = employee.name
            res["employee_id"] = employee.id
        else:
            msg = _("No employee found with card %s") % card_code
            _logger.warning(msg)
            res["error_message"] = msg
            return res
        try:
            attendance = employee._attendance_action_change()
            if attendance:
                msg = _("Attendance recorded for employee %s") % employee.name
                _logger.debug(msg)
                res["logged"] = True
                if attendance.check_out:
                    res["action"] = "check_out"
                else:
                    res["action"] = "check_in"
                return res
            else:
                msg = _("No attendance was recorded for employee %s") % employee.name
                _logger.error(msg)
                res["error_message"] = msg
                return res
        except Exception as e:
            res["error_message"] = repr(e)
            _logger.error(repr(e))
        return res
