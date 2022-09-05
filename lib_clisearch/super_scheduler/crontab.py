from typing import Union, Optional, Tuple

import pydantic
from pydantic import Field
from pydantic import validator, root_validator, BaseModel


class CrontabScheduleFormat(BaseModel):

    # schedule
    minute: str = Field(
        default="*",
        description="minute",
        example="--minute 50"
    )
    hour: str = Field(
        default="*",
        description="hour",
        example="--hour 10"
    )
    day_of_week: str = Field(
        default="*",
        description="day of week",
        example="--day_of_week mon,wed"
    )
    day_of_month: str = Field(
        default="*",
        description="day of month",
        example="--day_of_month 17,20"
    )
    month_of_year: str = Field(
        default="*",
        description="month of year",
        example="--month_of_year 1,3"
    )
    crontab_line: Optional[str] = Field(
        default=None,
        description="crontab line",
        example="--crontab_line \"32 18 mon,wed 17,21,29 *\""
    )

    @validator('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year', 'crontab_line', pre=True)
    def time_range_validator(cls, value, field):
        field: pydantic.fields.ModelField
        field_name = field.name
        field_type = field.type_
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Set only one '{field_name}' argument: '--{field_name} \"smth...\"'")
            value = field_type(value[0])
        return value

    @root_validator()
    def transform_crontab_line(cls, values):
        if not values.get('crontab_line'):
            return values
        crontab_line = values['crontab_line']
        crontab_line = crontab_line.split(' ')
        if len(crontab_line) != 5:
            raise ValueError(f"Enter 5 params in crontab line. Got {crontab_line} "
                             "Example: '32 18 mon,wed 17,21,29 * *', '10 * * * *'")
        schedule_time_params = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')
        for param, value in zip(schedule_time_params, crontab_line):
            values[param] = value
        return values