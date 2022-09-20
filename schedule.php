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
            }
            body
            {
                font-size: 25px;
            }
            h1{
                text-align: center;
            }
        </style>
    </head>
    <body>
        <table>
            <?php
                $myfile = file_get_contents('C:\xampp\htdocs\data\schedule\schedule.json');
                $json_arr = json_decode($myfile, true);
                echo '
                    <h1>'.$json_arr['Information']['Schedule_date'].'</h1>
                    <br>
                    <h1>'.$json_arr['Information']['Group_name'].'</h1>';
                echo '<tr><td>Номер пары</td><td>Пара, Преподаватель</td><td>Кабинет</td></tr>';
                for ($i = 0; $i < count($json_arr) - 1; $i++)
                {
                    echo '<tr>';
                    echo '<td>'.$json_arr['Number_'.$i]['Lesson_number'].'</td>';
                    echo '<td>'.$json_arr['Number_'.$i]['Lesson'].'</td>';
                    echo '<td>'.$json_arr['Number_'.$i]['Cabinet'].'</td>';
                    echo '</tr>';
                }
            ?>
        </table>
    </body>
</html>
