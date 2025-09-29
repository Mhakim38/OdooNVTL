from odoo import models, fields, api
import os
import base64
import tempfile
import pandas as pd

class ImportCircularFilesWizard(models.TransientModel):
    _name = "import.circular.files.wizard"
    _description = "Import Circular Files Wizard"

    folder_path = fields.Char("Folder Path", required=True, help="Absolute path to the folder containing files")
    excel_file = fields.Binary("Excel Mapping File", required=True)
    excel_filename = fields.Char("Excel Filename")

    result_message = fields.Text("Result", readonly=True)

    def action_import_files(self):
        Circular = self.env['company.circular']
        CircularFile = self.env['circular.file']

        # save Excel temporarily
        temp_fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
        with open(temp_path, "wb") as f:
            f.write(base64.b64decode(self.excel_file))

        # read mapping
        df = pd.read_excel(temp_path)
        if "filename" not in df.columns or "mysql_sequence" not in df.columns:
            raise ValueError("Excel must have 'filename' and 'mysql_sequence' columns.")

        success, skipped_files, missing_circulars = 0, [], []

        for _, row in df.iterrows():
            fname = str(row["filename"]).strip()
            mysql_seq = int(row["mysql_sequence"])
            fpath = os.path.join(self.folder_path, fname)

            # check if file exists
            if not os.path.isfile(fpath):
                skipped_files.append(fname)
                continue

            # find circular
            circular = Circular.search([('mysql_sequence', '=', mysql_seq)], limit=1)
            if not circular:
                missing_circulars.append(f"{fname} -> mysql_sequence {mysql_seq}")
                continue

            # create attachment
            with open(fpath, "rb") as f:
                file_content = f.read()

            attachment = self.env['ir.attachment'].create({
                'name': fname,
                'datas': base64.b64encode(file_content),
                'res_model': 'company.circular',
                'res_id': circular.id,
            })

            # link to circular.file
            CircularFile.create({
                'circular_id': circular.id,  # link to the circular
                'attachment_ids': [(4, attachment.id)],  # link files
            })

            success += 1

        # prepare log message
        msg = f"✅ Imported: {success}\n"
        if skipped_files:
            msg += f"\n⚠ Missing Files ({len(skipped_files)}): {', '.join(skipped_files)}"
        if missing_circulars:
            msg += f"\n❌ No Circular Found ({len(missing_circulars)}): {', '.join(missing_circulars)}"

        # show result in wizard
        self.result_message = msg

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.circular.files.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
