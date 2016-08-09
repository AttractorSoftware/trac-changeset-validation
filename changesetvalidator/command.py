import json
import re
import sys
from trac.core import *
from trac.admin.api import IAdminCommandProvider
from trac.resource import ResourceNotFound
from trac.ticket import Ticket


class ChangesetValidatorCommand(Component):
    """trac-admin command provider for changeset validation."""
    implements(IAdminCommandProvider)

    def get_admin_commands(self):
        yield ('changeset validate_messages', '<repository> <message_data>',
               """Validate changeset message(s) against tickets mentioned in messages

                This command should appear in the list of commands
               """,
               self.complete, self.validate)

    def validate(self, repository, message_data):
        messages = json.loads(message_data)
        error_messages = []
        for commit_id, message in messages.items():
            changeset_message = self._build_changeset_message(message)
            if changeset_message.is_declined():
                error_messages.append('Commit ID ' + commit_id + " is declined: \n" +
                                      changeset_message.get_errors_text())
            else:
                self._log_debug_message('Commit ID ' + commit_id + " passed: \n" +
                                        changeset_message.get_errors_text())

        if len(error_messages) > 0:
            self._print_error_messages(error_messages)
            return -1

        return 0

    def complete(self, args):
        pass

    def _print_to_stderr(self, message):
        print >> sys.stderr, message
        self._log_debug_message(message)

    def _log_debug_message(self, message):
        self.env.log.debug('[ChangesetValidatorPlugin] ' + message)

    def _build_changeset_message(self, message):
        return ChangesetMessage(self.env, self.config, message)

    def _print_error_messages(self, error_messages):
        for error_message in error_messages:
            self._print_to_stderr('============ Changeset message validation error ===============')
            self._print_to_stderr(error_message)
            self._print_to_stderr('===============================================================')


class ChangesetMessage:

    env = None
    config = None
    _message = ''
    _errors = []
    _valid_tickets = 0

    def __init__(self, env, config, message):
        self.env = env
        self.config = config
        self._message = message
        self._find_errors()

    def is_declined(self):

        if self._valid_tickets == 0 and not self._is_merge_commit():
            return True

        return False

    def get_errors(self):
        return self._errors

    def _is_merge_commit(self):
        return re.match("^merge", self._message, flags=re.IGNORECASE) is not None

    def get_errors_text(self):
        text = []
        for error in self._errors:
            text.append('   ' + error)

        return "\n".join(text)

    def _find_errors(self):
        self._errors = []
        tickets = 0
        for ticket_number in self._find_ticket_number_in_message():
            try:
                ticket = Ticket(self.env, ticket_number)
                statuses_allowing_commits = self._get_valid_ticket_states()

                if ticket["status"] not in statuses_allowing_commits:
                    self._errors.append('Ticket #' + str(ticket_number) + ' is not ' +
                                        ' or '.join(statuses_allowing_commits))
                else:
                    self._valid_tickets += 1
            except ResourceNotFound: # ticket does not exist
                self._errors.append("Ticket #" + str(ticket_number) + "doesn't exist")

            tickets += 1

        if tickets == 0:
            self._errors.append("No tickets defined in message")

    def _find_ticket_number_in_message(self):
        r = re.compile("#(\d+)")
        for match in r.finditer(self._message):
            yield int(match.group(1))

    def _get_valid_ticket_states(self):
        valid_states = self.config.getlist('changeset-validator', 'valid_ticket_states')
        return valid_states
