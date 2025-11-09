MAIL_MSG = """
<!DOCTYPE html>
    <html >
    <head>
    <meta charset="UTF-8">
    <title>Responsive Table</title>
        <style>
            table {
            border-spacing: 1;
            border-collapse: collapse;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            max-width: 100%;
            width: 100%;
            margin: 0 auto;
            position: relative;
            }
            table * {
            position: relative;
            }
            table td,
            table th {
            padding-left: 8px;
            }
            table thead tr {
            height: 30px;
            background: #99cc33;
            font-size: 16px;
            }
            table tbody tr {
            height: 48px;
            border: 1px solid #e3f1d5;
            border-right: 1px solid #e3f1d5;
            }
            /* table tbody tr:last-child {
            border: 0;
            } */
            table td,
            table th {
            text-align: left;
            }
            table td.l,
            table th.l {
            text-align: right;
            }
            table td.c,
            table th.c {
            text-align: center;
            }
            table td.r,
            table th.r {
            text-align: center;
            }

            @media screen and (max-width: 35.5em) {
            table {
                display: block;
            }
            table > *,
            table tr,
            table td,
            table th {
                display: block;
            }
            table thead {
                display: none;
            }
            table tbody tr {
                height: auto;
                padding: 8px 0;
            }
            table tbody tr td {
                padding-left: 45%;
                margin-bottom: 12px;
            }
            table tbody tr td:last-child {
                margin-bottom: 0;
            }
            table tbody tr td:before {
                position: absolute;
                font-weight: 700;
                width: 40%;
                left: 10px;
                top: 0;
            }
            table tbody tr td:nth-child(1):before {
                content: "Git Usage";
            }
            table tbody tr td:nth-child(2):before {
                content: "Time Logged";
            }
            table tbody tr td:nth-child(3):before {
                content: "Status";
            }
            
            }
            body {
            /* background: #99cc33; */
            font: 400 14px "Calibri", "Arial";
            padding: 20px;
            }

            blockquote {
            color: rgb(0, 0, 0);
            text-align: center;
            
            }

        </style>
    
    </head>

    <h3>Git Usage Report</h3>
    <table>
        <thead>
            <tr>
            <th width="30%">Organization</th>
            <th width="40%">Total Git Usage</th>
            <th>Time Logged</th>
            

            </tr>
        <thead>
        <tbody>
            <tr><td><strong>${org}</strong></td><td>${usage_i} GB</td><td>${usage_i_time}</td></tr>
            <tr><td><strong>${org}</strong></td><td>${usage_f} GB</td><td>${usage_f_time}</td></tr>
        </tbody>
        </table><br/>
    <h3>Current Usage Statistics</h3>
    
        <table>
        <thead>
            <tr>
            <th width="30%">Public Git Usage</th>
            <th width="40%">Private Git Usage</th>
            <th>Usage Change</th>

            </tr>
        <thead>
        <tbody>
            <tr><td>${public_usage} GB</td><td>${private_usage} GB</td><td>${usage_change} GB</td></tr>
            <tr><td>${public_usage_x} %</td><td>${private_usage_x} %</td><td>${usage_change_x} %</td></tr>
        </tbody>
        </table>

        <br/>

        <blockquote>System generated report
        </blockquote>
        
    
    </body>
    </html>
"""