from datetime import datetime

from astm.mapping import (
    Record, ConstantField, DateTimeField, IntegerField, NotUsedField,
    TextField, RepeatedComponentField, Component
)


QuidelHeaderRecord = Record.build(
    ConstantField(name='type', default='H'),  # 1
    RepeatedComponentField(Component.build(
        ConstantField(name='_', default=''),
        TextField(name='__')
    ), name='delimeter', default=[[], ['', '&']]),  # 2
    NotUsedField(name='unused01'), # 3
    NotUsedField(name='unused02'), # 4
    TextField(name='instrument'),  # 5
    NotUsedField(name='unused03'), # 6
    NotUsedField(name='unused03'), # 7
    NotUsedField(name='unused03'), # 8
    NotUsedField(name='unused03'), # 9
    NotUsedField(name='unused03'), # 10
    NotUsedField(name='unused03'), # 11
    ConstantField(name='processing_id', default='P'),  # 12
    TextField(name='firmware'),  # 13
    DateTimeField(name='timestamp', default=datetime.now, required=True),  # 14
)


QuidelPatientRecord =  Record.build(
    ConstantField(name='type', default='P'),  # 1
    IntegerField(name='seq', default=1, required=True),  # 2
    TextField(name='patient_id'),  # 3
    NotUsedField(name='unused00'), # 4
    NotUsedField(name='unused01'),
    NotUsedField(name='unused02'),
    NotUsedField(name='unused03'),
    NotUsedField(name='unused04'),
    NotUsedField(name='unused05'),
    NotUsedField(name='unused06'), # 10
    NotUsedField(name='unused07'),
    NotUsedField(name='unused08'),
    NotUsedField(name='unused09'),
    NotUsedField(name='unused10'),
    NotUsedField(name='unused11'),
    NotUsedField(name='unused12'),
    NotUsedField(name='unused13'),
    NotUsedField(name='unused14'),
    NotUsedField(name='unused15'),
    NotUsedField(name='unused16'), # 20
    NotUsedField(name='unused17'),
    NotUsedField(name='unused18'),
    NotUsedField(name='unused19'),
    NotUsedField(name='unused20'),
    NotUsedField(name='unused21'), # 25
    TextField(name='location'),
)

QuidelOrderRecord = Record.build(
    ConstantField(name='type', default='O'),  # 1
    IntegerField(name='seq', default=1, required=True),  # 2
    TextField(name='order_id'),  # 3
    NotUsedField(name='unused00'),  # 4
    TextField(name='test_type'),  # 5
    NotUsedField(name='unused01'),
    NotUsedField(name='unused02'),
    NotUsedField(name='unused03'),
    NotUsedField(name='unused04'),
    NotUsedField(name='unused05'),  # 10
    TextField(name='operator_id'),  # 11
    NotUsedField(name='unused06'),  # 12
    NotUsedField(name='unused07'),  # 13
    NotUsedField(name='unused08'),  # 14
    NotUsedField(name='unused09'),  # 15
    TextField(name='sample_type'),  # 16
)

QuidelCommentRecord = Record.build(
    ConstantField(name='type', default='C'),
    IntegerField(name='seq', default=1, required=True),
    NotUsedField(name='unused00'),
    TextField(name='sample_comment'),
)

QuidelResultRecord = Record.build(
    ConstantField(name='type', default='R'),  # 1
    IntegerField(name='seq', default=1, required=True),  # 2
    TextField(name='analyte_name'),  # 3
    TextField(name='test_value'),  # 4
    TextField(name='test_units'),  # 5
    TextField(name='test_range'),  # 6
    TextField(name='test_flag'),  # 7
    NotUsedField(name='unused00'),  # 8
    TextField(name='test_type'),  # 9
    NotUsedField(name='unused01'),  # 10
    NotUsedField(name='unused02'),  # 11
    NotUsedField(name='unused03'),  # 12
    DateTimeField(name='completion'),  #13
)