# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from contextlib import contextmanager
from typing import Type

from ..game.player import Player
from ..log import LogStream, NullLogger
from ..game import Action, PlayerColor, PlayerException
from .client import RemoteProcessClassClient, AsyncProcessStatus, \
    WrappedProcessException
from .resources import ResourceLimitException

RECV_TIMEOUT = 60 # Max seconds for reply from agent (wall clock time)

# Provide a wrapper for Agent classes to handle tedious details like timing,
# measuring space usage, reporting which method is currently being executed,
# etc. Note that Agents are run in a separate process to the referee, so that
# they cannot interfere with the referee's execution. See the AgentProcess
# (process.py) class for more details.

class AgentProxyPlayer(Player):

    def __init__(self, 
        name: str,
        color: PlayerColor, 
        agent_loc: tuple[str, str], 
        time_limit: float | None, 
        space_limit: float | None, 
        log: LogStream=NullLogger(),
        intercept_exc_type: Type[Exception]=PlayerException
    ):
        super().__init__(color)

        assert isinstance(agent_loc, tuple), "agent_loc must be a tuple"
        assert len(agent_loc) == 2, "agent_loc must be a tuple (pkg, cls)"
        self._pkg, self._cls = agent_loc
        
        self._name = name
        self._agent: RemoteProcessClassClient = RemoteProcessClassClient(
            self._pkg, self._cls, 
            time_limit=time_limit, space_limit=space_limit, 
            recv_timeout=RECV_TIMEOUT, 
            log=log,
            # Class constructor arguments
            color=color
        )
        self._log = log
        self._ret_symbol = f"⤷" if log.setting("unicode") else "->"
        self._InterceptExc = intercept_exc_type

    @contextmanager
    def _intercept_exc(self):
        try:
            yield

        # Reraising exceptions as PlayerExceptions to determine win/loss
        # outcomes in calling code (see the 'game' module).
        except ResourceLimitException as e:
            self._log.error(f"resource limit exceeded (pid={self._agent.pid}): {str(e)}")
            self._log.error("\n")
            self._log.error(self._summarise_status(self._agent.status))
            self._log.error("\n")

            raise self._InterceptExc(
                f"resource limit exceeded in {self._name} agent class",
                self._color
            )

        except WrappedProcessException as e:
            err_lines = str(e.args[1]["stacktrace_str"]).splitlines()

            self._log.error(f"exception caught (pid={self._agent.pid}):")
            self._log.error("\n")
            self._log.error("\n".join([f">> {line}" for line in err_lines]))
            self._log.error("\n")

            raise self._InterceptExc(
                f"error in {self._name} agent class\n"
                f"{self._ret_symbol} {err_lines[-1]}",
                self._color
            )

    async def __aenter__(self) -> 'AgentProxyPlayer':
        # Import the agent class (in a separate process). Note: We are wrapping
        # another async context manager here, so need to use the __aenter__ and
        # __aexit__ methods.
        self._log.debug(f"creating agent subprocess...")
        with self._intercept_exc():
            await self._agent.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._agent.__aexit__(exc_type, exc_value, traceback)
        self._log.debug(f"agent process terminated")

    async def action(self) -> Action:
        self._log.debug(f"call 'action()'...")

        with self._intercept_exc():
            action: Action = await self._agent.action()

        self._log.debug(f"{self._ret_symbol} {action!r}")
        self._log.debug(self._summarise_status(self._agent.status))
        return action

    async def turn(self, color: PlayerColor, action: Action):
        self._log.debug(f"call 'turn({color!r}, {action!r})'...")

        with self._intercept_exc():
            await self._agent.turn(color, action)

        self._log.debug(self._summarise_status(self._agent.status))

    def _summarise_status(self, status: AsyncProcessStatus | None):
        if status is None:
            return "resources usage status: unknown\n"

        time_str = f"  time:  +{status.time_delta:6.3f}s  (just elapsed)   "\
                   f"  {status.time_used:7.3f}s  (game total)\n"
        space_str = ""
        if status.space_known:
            space_str = f"  space: {status.space_curr:7.3f}MB (current usage)  "\
                        f"  {status.space_peak:7.3f}MB (peak usage)\n"
        else:
            space_str = "  space: unknown (check platform)\n"
        return f"resources usage status:\n{time_str}{space_str}"
