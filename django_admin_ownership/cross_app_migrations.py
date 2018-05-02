from django.db import migrations, models
import django.db.models.deletion

from django.db.migrations.operations.base import Operation

class WithAppLabelOperation(Operation):
    @property
    def reduces_to_sql(self):
        self.op.reduces_to_sql
    @property
    def reversible(self):
        self.op.reversible

    def __init__(self, app_label, op):
        self.app_label = app_label
        self.op = op
        
    def state_forwards(self, app_label, state):
        return self.op.state_forwards(self.app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self.op.database_forwards(self.app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self.op.database_backwards(self.app_label, schema_editor, from_state, to_state)

    def describe(self):
        return self.op.describe()
