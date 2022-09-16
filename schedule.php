<html>
    <head>
        <meta charset="utf-8">
        <title>Schedule</title>
        <style>
            table, td
            {
                margin: auto;
                border-collapse: collapse;
                border: 2px solid;
                padding: 7px;
                width: 1000px;
                height: 80px;
                font-size: 25px;
            }
        </style>
    </head>
    <body>
        <table>
            <?php
                $myfile = file_get_contents('C:\xampp\htdocs\data\schedule\schedule.json');
                $json_arr = json_decode($myfile, true);
                echo '<tr><td>Номер пары</td><td>Пара, Преподаватель</td><td>Кабинет</td></tr>';
                foreach ($json_arr as $arr)
                {
                    echo '<tr>';
                    echo '<td>'.$arr['Lesson_number'].'</td>';
                    echo '<td>'.$arr['Lesson'].'</td>';
                    echo '<td>'.$arr['Cabinet'].'</td>';
                    echo '</tr>';
                } 
            ?>
        </table>
    </body>
</html>