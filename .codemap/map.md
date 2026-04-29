# Code Map — bff-python-web-skeleton

**102 files** | **8,734 lines** | **136 classes** | **172 functions** | commit `c64f0d56d778`

Symbols ranked by PageRank (most-connected first).

## Dependencies

  backend.services.sync -> backend.core.encryption, backend.core.logging, backend.core.utils, backend.repositories.exchange_connection, backend.repositories.fill, backend.repositories.position, backend.services.exchange.factory, backend.services.grouper.engine, backend.services.grouper.reconciler, backend.services.sync_events
  backend.migrations.env -> backend.models.base, backend.models.candle, backend.models.exchange_connection, backend.models.fill, backend.models.magic_link, backend.models.position, backend.models.position_attachment, backend.models.position_note, backend.models.user
  backend.models -> backend.models.base, backend.models.candle, backend.models.exchange_connection, backend.models.fill, backend.models.magic_link, backend.models.position, backend.models.position_attachment, backend.models.position_note, backend.models.user
  backend.api.v1.endpoints.attachments -> backend.core.config, backend.core.dependencies, backend.core.exceptions, backend.core.logging, backend.schemas.attachment, backend.schemas.base, backend.services.journal, backend.services.storage
  backend.services.views -> backend.core.config, backend.core.logging, backend.repositories.exchange_connection, backend.repositories.fill, backend.repositories.position, backend.repositories.position_attachment, backend.repositories.position_note
  backend.api.v1.endpoints.views -> backend.core.dependencies, backend.core.logging, backend.schemas.base, backend.schemas.views, backend.services.storage, backend.services.views
  backend.main -> backend.api, backend.api.v1, backend.core.config, backend.core.exception_handlers, backend.core.logging, backend.core.middleware
  backend.services.auth -> backend.core.config, backend.core.logging, backend.core.security, backend.core.utils, backend.repositories.magic_link, backend.repositories.user
  backend.services.journal -> backend.core.config, backend.core.exceptions, backend.core.logging, backend.repositories.position, backend.repositories.position_attachment, backend.repositories.position_note
  backend.api.v1.endpoints.auth -> backend.core.dependencies, backend.core.logging, backend.schemas.auth, backend.schemas.base, backend.services.auth
  backend.api.v1.endpoints.connections -> backend.core.dependencies, backend.core.logging, backend.schemas.base, backend.schemas.connection, backend.services.connection
  backend.api.v1.endpoints.notes -> backend.core.dependencies, backend.core.logging, backend.schemas.base, backend.schemas.note, backend.services.journal
  backend.api.v1.endpoints.positions -> backend.core.dependencies, backend.core.logging, backend.schemas.base, backend.schemas.position, backend.services.journal
  backend.services.connection -> backend.core.encryption, backend.core.exceptions, backend.core.logging, backend.repositories.exchange_connection, backend.services.exchange.factory
  backend.api.v1.endpoints.users -> backend.core.dependencies, backend.schemas.auth, backend.schemas.base, backend.services.user
  backend.core.security -> backend.core.config, backend.core.exceptions, backend.core.logging, backend.core.utils
  backend.api.health -> backend.core.health, backend.core.logging, backend.core.utils
  backend.api.v1.endpoints.events -> backend.core.logging, backend.core.security, backend.services.sync_events
  backend.api.v1.endpoints.export -> backend.core.dependencies, backend.core.logging, backend.services.views
  backend.core.exception_handlers -> backend.core.exceptions, backend.core.logging, backend.schemas.base
  backend.repositories.base -> backend.core.exceptions, backend.core.logging, backend.models.base
  backend.repositories.magic_link -> backend.core.utils, backend.models.magic_link, backend.repositories.base
  backend.services.exchange.binance_futures -> backend.core.config, backend.core.logging, backend.services.exchange.types
  backend.services.exchange.bybit -> backend.core.config, backend.core.logging, backend.services.exchange.types
  backend.core.dependencies -> backend.core.database, backend.core.logging
  backend.core.encryption -> backend.core.config, backend.core.logging
  backend.core.health -> backend.core.logging, backend.core.utils
  backend.core.middleware -> backend.core.logging, backend.core.utils
  backend.core.rate_limiter -> backend.core.logging, backend.core.utils
  backend.models.fill -> backend.core.utils, backend.models.base
  backend.models.magic_link -> backend.core.utils, backend.models.base
  backend.models.position_attachment -> backend.core.utils, backend.models.base
  backend.repositories.exchange_connection -> backend.models.exchange_connection, backend.repositories.base
  backend.repositories.fill -> backend.models.fill, backend.repositories.base
  backend.repositories.position -> backend.models.position, backend.repositories.base
  backend.repositories.position_attachment -> backend.models.position_attachment, backend.repositories.base
  backend.repositories.position_note -> backend.models.position_note, backend.repositories.base
  backend.repositories.user -> backend.models.user, backend.repositories.base
  backend.services.base -> backend.core.exceptions, backend.core.logging
  backend.services.email -> backend.core.config, backend.core.logging
  backend.services.exchange.factory -> backend.core.logging, backend.services.exchange.protocol
  backend.services.exchange.rate_limiter -> backend.core.logging, backend.core.rate_limiter
  backend.services.grouper.engine -> backend.services.exchange.types, backend.services.grouper.types
  backend.services.grouper.reconciler -> backend.core.logging, backend.services.grouper.types
  backend.services.indicators.engine -> backend.services.indicators.definitions, backend.services.indicators.registry
  backend.services.storage -> backend.core.config, backend.core.logging
  backend.tasks.calculate_indicators -> backend.core.logging, backend.tasks.broker
  backend.tasks.cleanup -> backend.core.logging, backend.tasks.broker
  backend.tasks.sync_trades -> backend.core.logging, backend.tasks.broker
  backend.api.v1 -> backend.api.v1.endpoints
  backend.core.concurrency -> backend.core.logging
  backend.core.config -> backend.core.config_schema
  backend.core.database -> backend.core.logging
  backend.core.logging -> backend.core.config
  backend.core.pagination -> backend.schemas.base
  backend.core.resilience -> backend.core.logging
  backend.events.broker -> backend.core.logging
  backend.events.middleware -> backend.core.logging
  backend.events.publishers -> backend.core.logging
  backend.events.schemas -> backend.core.utils
  backend.models.base -> backend.core.utils
  backend.models.candle -> backend.models.base
  backend.models.exchange_connection -> backend.models.base
  backend.models.position -> backend.models.base
  backend.models.position_note -> backend.models.base
  backend.models.user -> backend.models.base
  backend.repositories -> backend.repositories.base
  backend.repositories.candle -> backend.models.candle
  backend.schemas -> backend.schemas.base
  backend.schemas.base -> backend.core.utils
  backend.schemas.views -> backend.schemas.position
  backend.services.exchange.protocol -> backend.services.exchange.types
  backend.services.indicators.definitions -> backend.services.indicators.registry
  backend.services.sync_events -> backend.core.logging
  backend.services.user -> backend.repositories.user
  backend.tasks.broker -> backend.core.logging
  backend.tasks.scheduler -> backend.core.logging

## backend

modules/backend/core/config.py (237 lines):
│class Settings(BaseSettings):
│    db_password: str
│    redis_password: str
│    app_secret_key: str
│    encryption_key: str
│    resend_api_key: str
│    frontend_url: str
│    s3_endpoint: str
│    s3_bucket: str
│    s3_access_key: str
│    s3_secret_key: str
│    s3_region: str
│    anthropic_api_key: str
│class AppConfig:
│    def __init__() -> None
│    def application() -> ApplicationSchema
│    def database() -> DatabaseSchema
│    def logging() -> LoggingSchema
│    def features() -> FeaturesSchema
│    def security() -> SecuritySchema
│    def observability() -> ObservabilitySchema
│    def concurrency() -> ConcurrencySchema
│    def events() -> EventsSchema
│    def exchange() -> ExchangeSchema
│    def sync() -> SyncSchema
│    def indicators() -> IndicatorsSchema
│    def journal() -> JournalConfigSchema
│    def candles() -> CandlesSchema
│def find_project_root() -> Path
│def validate_project_root() -> Path
│def load_yaml_config(filename: str) -> dict[str, Any]
│def _load_validated(schema_cls: type, filename: str) -> Any
│@lru_cache
│def get_settings() -> Settings
│@lru_cache
│def get_app_config() -> AppConfig
│def get_database_url(async_driver: bool) -> str
│def get_redis_url() -> str
│def get_server_base_url() -> tuple[str, float]

modules/backend/core/logging.py (278 lines):
│def _load_logging_config() -> dict[str, Any]
│def _get_logging_config() -> dict[str, Any]
│def _resolve_log_path(configured_path: str) -> Path
│def add_trace_context(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]
│def setup_logging(level: str | None, format_type: str | None, enable_console: bool | None, ...) -> None
│def get_logger(name: str) -> Any
│def log_with_source(logger: Any, source: str, level: str, ...) -> None

modules/backend/core/config_schema.py (366 lines):
│class _StrictBase(BaseModel):
│class ApplicationSchema(_StrictBase):
│    name: str
│    version: str
│    description: str
│    environment: str
│    debug: bool
│    api_prefix: str
│    docs_enabled: bool
│    server: ServerSchema
│    cors: CorsSchema
│    pagination: PaginationSchema
│    timeouts: TimeoutsSchema
│class DatabaseSchema(_StrictBase):
│    host: str
│    port: int
│    name: str
│    user: str
│    pool_size: int
│    max_overflow: int
│    pool_timeout: int
│    pool_recycle: int
│    echo: bool
│    echo_pool: bool
│    redis: RedisSchema
│class LoggingSchema(_StrictBase):
│    level: str
│    format: str
│    handlers: HandlersSchema
│class FeaturesSchema(_StrictBase):
│    auth_magic_link_enabled: bool
│    auth_rate_limit_enabled: bool
│    api_detailed_errors: bool
│    api_request_logging: bool
│    security_headers_enabled: bool
│    security_cors_enforce_production: bool
│    background_tasks_enabled: bool
│    events_enabled: bool
│    events_publish_enabled: bool
│    observability_tracing_enabled: bool
│    observability_metrics_enabled: bool
│class SecuritySchema(_StrictBase):
│    jwt: JwtSchema
│    rate_limiting: RateLimitingSchema
│    request_limits: RequestLimitsSchema
│    headers: SecurityHeadersSchema
│    secrets_validation: SecretsValidationSchema
│    cors: CorsEnforcementSchema
│class ObservabilitySchema(_StrictBase):
│    tracing: TracingSchema
│    metrics: MetricsSchema
│    health_checks: HealthChecksSchema
│class ConcurrencySchema(_StrictBase):
│    thread_pool: ThreadPoolSchema
│    process_pool: ProcessPoolSchema
│    semaphores: SemaphoresSchema
│    shutdown: ShutdownSchema
│class EventsSchema(_StrictBase):
│    broker: EventBrokerSchema
│    streams: EventStreamsSchema
│    consumers: dict[str, ConsumerConfigSchema]
│    dlq: EventDlqSchema
│class ExchangeSchema(_StrictBase):
│    binance: ExchangeEndpointSchema
│    bybit: ExchangeEndpointSchema
│class SyncSchema(_StrictBase):
│    lock_ttl_seconds: int
│    lock_renewal_interval_seconds: int
│    first_sync_lookback_days: int
│    bybit_window_days: int
│class IndicatorsSchema(_StrictBase):
│    timeframes: list[str]
│    ema_periods: dict[str, list[int]]
│    lookback_bars: int
│    staleness_multiplier: int
│    avg_dollar_volume_period: int
│    oi_change_lookback_bars: int
│class JournalConfigSchema(_StrictBase):
│    valid_strategies: list[str]
│    max_attachments_per_position: int
│    max_image_size_bytes: int
│    max_storage_per_user_bytes: int
│class CandlesSchema(_StrictBase):
│    retention_months: int
│    use_timescaledb: bool
│    chunk_interval: str
│class RedisSchema(_StrictBase):
│    host: str
│    port: int
│    db: int
│    broker: BrokerSchema
│class HandlersSchema(_StrictBase):
│    console: ConsoleHandlerSchema
│    file: FileHandlerSchema
│class ExchangeEndpointSchema(_StrictBase):
│    base_url: str
│    rate_limit: dict[str, int]
│    timeout_seconds: int
│    max_retries: int
│    retry_base_seconds: int
│class BrokerSchema(_StrictBase):
│    queue_name: str
│    result_expiry_seconds: int
│class ApiRateLimitSchema(_StrictBase):
│    requests_per_minute: int
│    requests_per_hour: int
│class ConsoleHandlerSchema(_StrictBase):
│    enabled: bool
│class FileHandlerSchema(_StrictBase):
│    enabled: bool
│    path: str
│    max_bytes: int
│    backup_count: int
│class TracingSchema(_StrictBase):
│    enabled: bool
│    service_name: str
│    exporter: str
│    otlp_endpoint: str
│    sample_rate: float
│class MetricsSchema(_StrictBase):
│    enabled: bool
│class HealthChecksSchema(_StrictBase):
│    ready_timeout_seconds: int
│    detailed_auth_required: bool
│class ConsumerCircuitBreakerSchema(_StrictBase):
│    fail_max: int
│    timeout_duration: int
│class ConsumerRetrySchema(_StrictBase):
│    max_attempts: int
│    backoff_multiplier: int
│    backoff_max: int
│class ServerSchema(_StrictBase):
│    host: str
│    port: int
│class CorsSchema(_StrictBase):
│    origins: list[str]
│class PaginationSchema(_StrictBase):
│    default_limit: int
│    max_limit: int
│class TimeoutsSchema(_StrictBase):
│    database: int
│    external_api: int
│    background: int
│class ThreadPoolSchema(_StrictBase):
│    max_workers: int
│class ProcessPoolSchema(_StrictBase):
│    max_workers: int
│class SemaphoresSchema(_StrictBase):
│    database: int
│    redis: int
│    external_api: int
│    llm: int
│class ShutdownSchema(_StrictBase):
│    drain_seconds: int
│class EventBrokerSchema(_StrictBase):
│    type: str
│class EventStreamsSchema(_StrictBase):
│    default_maxlen: int
│class ConsumerConfigSchema(_StrictBase):
│    stream: str
│    group: str
│    criticality: str
│    circuit_breaker: ConsumerCircuitBreakerSchema
│    retry: ConsumerRetrySchema
│    processing_timeout: int
│class EventDlqSchema(_StrictBase):
│    enabled: bool
│    stream_prefix: str
│class JwtSchema(_StrictBase):
│    algorithm: str
│    access_token_expire_minutes: int
│    refresh_token_expire_days: int
│    audience: str
│class RateLimitingSchema(_StrictBase):
│    api: ApiRateLimitSchema
│class RequestLimitsSchema(_StrictBase):
│    max_body_size_bytes: int
│    max_header_size_bytes: int
│class SecurityHeadersSchema(_StrictBase):
│    x_content_type_options: str
│    x_frame_options: str
│    referrer_policy: str
│    hsts_enabled: bool
│    hsts_max_age: int
│class SecretsValidationSchema(_StrictBase):
│    app_secret_min_length: int
│class CorsEnforcementSchema(_StrictBase):
│    enforce_in_production: bool
│    allow_methods: list[str]
│    allow_headers: list[str]

modules/backend/core/utils.py (22 lines):
│def utc_now() -> datetime

modules/backend/models/base.py (45 lines):
│class Base(DeclarativeBase):
│class UUIDMixin:
│    id: Mapped[UUID]
│class TimestampMixin:
│    created_at: Mapped[datetime]
│    updated_at: Mapped[datetime]

modules/backend/repositories/base.py (83 lines):
│class BaseRepository:
│    model: type[ModelType]
│    def __init__(session: AsyncSession) -> None
│    def get_by_id(id: UUID) -> ModelType
│    def get_by_id_or_none(id: UUID) -> ModelType | None
│    def create() -> ModelType
│    def update(id: UUID) -> ModelType
│    def delete(id: UUID) -> None
│    def exists(id: UUID) -> bool
│    def count() -> int

modules/backend/core/exceptions.py (72 lines):
│class ApplicationError(Exception):
│    def __init__(message: str, code: str) -> None
│class NotFoundError(ApplicationError):
│    def __init__(entity: str, id: str | None) -> None
│class ValidationError(ApplicationError):
│    def __init__(message: str, details: dict | None) -> None
│class AuthenticationError(ApplicationError):
│    def __init__(message: str) -> None
│class AuthorizationError(ApplicationError):
│    def __init__(message: str) -> None
│class ConflictError(ApplicationError):
│    def __init__(message: str) -> None
│class ExternalServiceError(ApplicationError):
│    def __init__(message: str) -> None
│class RateLimitError(ApplicationError):
│    def __init__(message: str) -> None
│class DatabaseError(ApplicationError):
│    def __init__(message: str) -> None

modules/backend/schemas/base.py (86 lines):
│class ApiResponse(BaseModel):
│    success: bool
│    data: DataT | None
│    error: ErrorDetail | None
│    metadata: ResponseMetadata
│class ResponseMetadata(BaseModel):
│    timestamp: datetime
│    request_id: str | None
│class ErrorDetail(BaseModel):
│    code: str
│    message: str
│    details: dict[str, Any] | None
│class ErrorResponse(BaseModel):
│    success: bool
│    data: None
│    error: ErrorDetail
│    metadata: ResponseMetadata
│class PaginatedResponse(BaseModel):
│    success: bool
│    data: list[DataT]
│    error: None
│    metadata: ResponseMetadata
│    pagination: 'PaginationInfo'
│class PaginationInfo(BaseModel):
│    total: int | None
│    limit: int
│    cursor: str | None
│    next_cursor: str | None
│    has_more: bool

modules/backend/services/exchange/types.py (69 lines):
│class RawFill:
│    exchange: str
│    product_type: str
│    symbol: str
│    exchange_trade_id: str
│    exchange_order_id: str
│    side: str
│    price: Decimal
│    quantity: Decimal
│    quote_quantity: Decimal
│    commission: Decimal
│    commission_asset: str
│    realised_pnl: Decimal | None
│    executed_at: datetime
│    raw_data: dict
│class CandleBar:
│    exchange: str
│    symbol: str
│    product_type: str
│    timeframe: str
│    open_time: datetime
│    open: Decimal
│    high: Decimal
│    low: Decimal
│    close: Decimal
│    volume: Decimal
│    quote_volume: Decimal
│    trade_count: int | None
│    open_interest: Decimal | None
│    oi_value: Decimal | None
│class FillPage:
│    fills: list[RawFill]
│    has_more: bool
│    cursor: dict | None
│class ConnectionTestResult:
│    success: bool
│    has_write_permission: bool
│    error: str | None
│    permissions: list[str]
│def exchange_ts_to_naive_utc(ms: int) -> datetime

modules/backend/services/indicators/registry.py (32 lines):
│class IndicatorDef:
│    name: str
│    compute_fn: Callable[[pd.DataFrame], object]
│    timeframes: list[str] | None
│def register(name: str, compute_fn: Callable[[pd.DataFrame], object], timeframes: list[str] | None) -> None
│def get_registered_indicators(timeframe: str) -> list[IndicatorDef]

modules/backend/core/dependencies.py (84 lines):
│def get_request_id(x_request_id: str | None) -> str
│def get_current_user(authorization: str | None, db: AsyncSession)
│def get_current_user_optional(authorization: str | None, db: AsyncSession)
│def get_refresh_token(refresh_token: str | None) -> str | None

modules/backend/tasks/broker.py (96 lines):
│def create_broker() -> 'ListQueueBroker'
│def get_broker() -> 'ListQueueBroker'
│def __getattr__(name: str)

modules/backend/repositories/user.py (24 lines):
│class UserRepository:
│    def get_by_email(email: str) -> User | None
│    def find_or_create_by_email(email: str) -> tuple[User, bool]

modules/backend/schemas/position.py (39 lines):
│class PositionSummary(BaseModel):
│    id: str
│    exchange: str
│    symbol: str
│    direction: str
│    status: str
│    strategy: str | None
│    entry_price_avg: str
│    exit_price_avg: str | None
│    total_entry_qty: str
│    realised_pnl: str | None
│    pnl_pct: float | None
│    hold_duration: str | None
│    opened_at: str
│    closed_at: str | None
│    tags: list[str]
│    rating: int | None
│class PositionUpdate(BaseModel):
│    strategy: str | None
│    tags: list[str] | None
│    rating: int | None
│class PositionDetail(PositionSummary):
│    total_exit_qty: str | None
│    total_commission: str
│    max_size_qty: str
│    indicators_at_open: dict | None
│    indicators_at_close: dict | None
│    is_user_modified: bool
│    entry_count: int
│    exit_count: int

modules/backend/models/user.py (14 lines):
│class User(Base, UUIDMixin, TimestampMixin):
│    email: Mapped[str]
│    display_name: Mapped[str | None]
│    is_active: Mapped[bool]

modules/backend/models/candle.py (30 lines):
│class Candle(Base):
│    exchange: Mapped[str]
│    symbol: Mapped[str]
│    product_type: Mapped[str]
│    timeframe: Mapped[str]
│    open_time: Mapped[datetime]
│    open: Mapped[Decimal]
│    high: Mapped[Decimal]
│    low: Mapped[Decimal]
│    close: Mapped[Decimal]
│    volume: Mapped[Decimal]
│    quote_volume: Mapped[Decimal]
│    trade_count: Mapped[int | None]
│    open_interest: Mapped[Decimal | None]
│    oi_value: Mapped[Decimal | None]

modules/backend/core/database.py (110 lines):
│def _create_engine() -> Any
│def get_engine() -> Any
│def get_session_factory() -> async_sessionmaker[AsyncSession]
│def get_db_session() -> AsyncGenerator[AsyncSession, None]
│@asynccontextmanager
│def get_async_session() -> AsyncGenerator[AsyncSession, None]

modules/backend/api/v1/endpoints/__init__.py (1 lines):

modules/backend/services/grouper/types.py (48 lines):
│class FillRole(str, Enum):
│class AssignedFill:
│    exchange_trade_id: str
│    role: FillRole
│    effective_qty: Decimal
│    price: Decimal
│    commission: Decimal
│    side: str
│    executed_at: datetime
│    symbol: str
│class GroupedPosition:
│    symbol: str
│    direction: str
│    status: str
│    entry_price_avg: Decimal
│    exit_price_avg: Decimal | None
│    total_entry_qty: Decimal
│    total_exit_qty: Decimal
│    total_commission: Decimal
│    realised_pnl: Decimal | None
│    max_size_qty: Decimal
│    opened_at: datetime
│    closed_at: datetime | None
│    fills: list[AssignedFill]

modules/backend/models/position.py (59 lines):
│class Position(Base, UUIDMixin, TimestampMixin):
│    user_id: Mapped[UUID]
│    connection_id: Mapped[UUID]
│    exchange: Mapped[str]
│    product_type: Mapped[str]
│    symbol: Mapped[str]
│    direction: Mapped[str]
│    status: Mapped[str]
│    strategy: Mapped[str | None]
│    entry_price_avg: Mapped[Decimal]
│    exit_price_avg: Mapped[Decimal | None]
│    total_entry_qty: Mapped[Decimal]
│    total_exit_qty: Mapped[Decimal | None]
│    total_commission: Mapped[Decimal]
│    realised_pnl: Mapped[Decimal | None]
│    max_size_qty: Mapped[Decimal]
│    opened_at: Mapped[datetime]
│    closed_at: Mapped[datetime | None]
│    indicators_at_open: Mapped[dict | None]
│    indicators_at_close: Mapped[dict | None]
│    tags: Mapped[list]
│    rating: Mapped[int | None]
│    is_user_modified: Mapped[bool]

modules/backend/models/exchange_connection.py (34 lines):
│class ExchangeConnection(Base, UUIDMixin, TimestampMixin):
│    user_id: Mapped[UUID]
│    exchange: Mapped[str]
│    product_types: Mapped[dict]
│    label: Mapped[str]
│    api_key_encrypted: Mapped[bytes]
│    api_secret_encrypted: Mapped[bytes]
│    api_key_nonce: Mapped[bytes]
│    api_secret_nonce: Mapped[bytes]
│    is_active: Mapped[bool]
│    last_sync_at: Mapped[datetime | None]
│    last_sync_cursor: Mapped[dict | None]
│    synced_symbols: Mapped[list]

modules/backend/models/position_attachment.py (38 lines):
│class PositionAttachment(Base, UUIDMixin):
│    position_id: Mapped[UUID]
│    user_id: Mapped[UUID]
│    attachment_type: Mapped[str]
│    file_key: Mapped[str | None]
│    file_name: Mapped[str | None]
│    file_size_bytes: Mapped[int | None]
│    mime_type: Mapped[str | None]
│    url: Mapped[str | None]
│    caption: Mapped[str | None]
│    created_at: Mapped[datetime]

modules/backend/models/position_note.py (29 lines):
│class PositionNote(Base, UUIDMixin, TimestampMixin):
│    position_id: Mapped[UUID]
│    user_id: Mapped[UUID]
│    note_type: Mapped[str]
│    content: Mapped[str]

modules/backend/models/fill.py (62 lines):
│class Fill(Base, UUIDMixin):
│    user_id: Mapped[UUID]
│    connection_id: Mapped[UUID]
│    position_id: Mapped[UUID | None]
│    exchange: Mapped[str]
│    product_type: Mapped[str]
│    symbol: Mapped[str]
│    exchange_trade_id: Mapped[str]
│    exchange_order_id: Mapped[str]
│    side: Mapped[str]
│    price: Mapped[Decimal]
│    quantity: Mapped[Decimal]
│    quote_quantity: Mapped[Decimal]
│    commission: Mapped[Decimal]
│    commission_asset: Mapped[str]
│    realised_pnl: Mapped[Decimal | None]
│    executed_at: Mapped[datetime]
│    raw_data: Mapped[dict]
│    created_at: Mapped[datetime]

modules/backend/services/exchange/protocol.py (48 lines):
│class ExchangeAdapter(Protocol):
│    def test_connection(api_key: str, api_secret: str) -> ConnectionTestResult
│    def fetch_fills_page(api_key: str, api_secret: str, symbol: str, product_type: str, cursor: dict | None) -> FillPage
│    def fetch_candles(symbol: str, product_type: str, timeframe: str, start_time: datetime, end_time: datetime | None, limit: int) -> list[CandleBar]
│    def fetch_open_interest(symbol: str, product_type: str, timeframe: str, start_time: datetime, limit: int) -> list[CandleBar]

modules/backend/models/magic_link.py (28 lines):
│class MagicLink(Base, UUIDMixin):
│    user_id: Mapped[UUID]
│    token_hash: Mapped[str]
│    expires_at: Mapped[datetime]
│    consumed_at: Mapped[datetime | None]
│    created_at: Mapped[datetime]

modules/backend/repositories/position.py (60 lines):
│class PositionRepository:
│    def get_by_user_filtered(user_id: UUID) -> list[Position]
│    def get_by_user_and_id(user_id: UUID, position_id: UUID) -> Position | None
│    def get_by_connection(connection_id: UUID) -> list[Position]

modules/backend/repositories/exchange_connection.py (33 lines):
│class ExchangeConnectionRepository:
│    def get_by_user(user_id: UUID) -> list[ExchangeConnection]
│    def get_by_user_and_id(user_id: UUID, connection_id: UUID) -> ExchangeConnection | None

modules/backend/core/security.py (120 lines):
│def create_access_token(data: dict[str, Any], expires_delta: timedelta | None) -> str
│def create_refresh_token(data: dict[str, Any]) -> str
│def create_sse_token(data: dict[str, Any]) -> str
│def decode_token(token: str, expected_type: str | None) -> dict[str, Any]
│def generate_magic_link_token() -> tuple[str, str]
│def hash_token(raw_token: str) -> str

modules/backend/services/journal.py (102 lines):
│class JournalService:
│    def __init__(session: AsyncSession) -> None
│    def update_position(position_id: UUID, user_id: UUID, strategy: str | None, tags: list[str] | None, rating: int | None) -> object
│    def create_note(position_id: UUID, user_id: UUID, note_type: str, content: str) -> object
│    def update_note(note_id: UUID, user_id: UUID, content: str) -> object
│    def delete_note(note_id: UUID, user_id: UUID) -> None
│    def _get_owned_position(position_id: UUID, user_id: UUID)

modules/backend/core/rate_limiter.py (60 lines):
│class RateLimitExceeded(Exception):
│    def __init__(limit: int, window_seconds: int) -> None
│def check_rate_limit(redis, key: str, limit: int, ...) -> None

modules/backend/services/indicators/definitions.py (120 lines):
│def _ema(period: int)
│def _prev_field(field: str)
│def _current_volume(df: pd.DataFrame) -> float | None
│def _trade_count(df: pd.DataFrame) -> int | None
│def _avg_dollar_volume(period: int)
│def _open_interest(df: pd.DataFrame) -> float | None
│def _oi_change_pct(lookback: int)

modules/backend/services/views.py (159 lines):
│class ViewService:
│    def __init__(session: AsyncSession) -> None
│    def get_dashboard(user_id: UUID) -> dict
│    def get_position_list(user_id: UUID) -> dict
│    def get_position_detail(user_id: UUID, position_id: UUID) -> dict
│    def get_connections(user_id: UUID) -> list
│    def get_settings(user_id: UUID, user) -> dict
│    def get_export_positions(user_id: UUID) -> list

modules/backend/schemas/auth.py (28 lines):
│class UserResponse(BaseModel):
│    id: str
│    email: str
│    display_name: str | None
│class AuthResponse(BaseModel):
│    access_token: str
│    sse_token: str
│    token_type: str
│    user: UserResponse
│class MagicLinkRequest(BaseModel):
│    email: EmailStr
│class VerifyRequest(BaseModel):
│    token: str
│class UpdateUserRequest(BaseModel):
│    display_name: str | None

modules/backend/repositories/position_attachment.py (39 lines):
│class PositionAttachmentRepository:
│    def get_by_position(position_id: UUID) -> list[PositionAttachment]
│    def count_by_position(position_id: UUID) -> int
│    def sum_size_by_user(user_id: UUID) -> int

modules/backend/repositories/position_note.py (21 lines):
│class PositionNoteRepository:
│    def get_by_position(position_id: UUID) -> list[PositionNote]

modules/backend/services/sync_events.py (46 lines):
│def channel_for_user(user_id: str) -> str
│def publish_sync_event(user_id: str, event_type: str, data: dict) -> None

modules/backend/core/encryption.py (46 lines):
│def load_encryption_key() -> bytes
│def encrypt(plaintext: str, key: bytes) -> tuple[bytes, bytes]
│def decrypt(ciphertext: bytes, nonce: bytes, key: bytes) -> str

modules/backend/core/health.py (89 lines):
│def check_database() -> dict[str, Any]
│def check_redis() -> dict[str, Any]

modules/backend/services/exchange/factory.py (39 lines):
│def register_adapter(exchange: str, adapter_cls: type) -> None
│def get_adapter(exchange: str) -> ExchangeAdapter
│def get_supported_exchanges() -> list[str]
│def _register_defaults() -> None

modules/backend/repositories/fill.py (37 lines):
│class FillRepository:
│    def upsert_fills(fills: list[dict]) -> int
│    def get_by_connection_sorted(connection_id: UUID) -> list[Fill]
│    def get_by_position(position_id: UUID) -> list[Fill]

modules/backend/services/storage.py (107 lines):
│def _get_s3_client()
│def _get_bucket() -> str
│def upload_file(user_id: str, position_id: str, file_data: bytes, ...) -> str
│def generate_presigned_url(file_key: str, expiry: int) -> str
│def delete_file(file_key: str) -> None
│def delete_user_files(user_id: str) -> int

modules/backend/services/user.py (20 lines):
│class UserService:
│    def __init__(session: AsyncSession) -> None
│    def update_profile(user_id: UUID, display_name: str | None) -> object
│    def deactivate(user_id: UUID) -> None

modules/backend/schemas/connection.py (28 lines):
│class ConnectionCreate(BaseModel):
│    exchange: str
│    product_types: list[str]
│    label: str
│    api_key: str
│    api_secret: str
│class ConnectionUpdate(BaseModel):
│    label: str | None
│    is_active: bool | None
│class ConnectionResponse(BaseModel):
│    id: str
│    exchange: str
│    product_types: list[str]
│    label: str
│    api_key_masked: str
│    is_active: bool
│    last_sync_at: str | None
│    synced_symbols: list[str]
│    created_at: str

modules/backend/schemas/note.py (21 lines):
│class NoteCreate(BaseModel):
│    note_type: str
│    content: str
│class NoteUpdate(BaseModel):
│    content: str
│class NoteResponse(BaseModel):
│    id: str
│    position_id: str
│    note_type: str
│    content: str
│    created_at: str
│    updated_at: str

modules/backend/services/auth.py (158 lines):
│class AuthService:
│    def __init__(session: AsyncSession, redis) -> None
│    def request_magic_link(email: str) -> tuple[str, str]
│    def verify_magic_link(raw_token: str) -> dict
│    def refresh_tokens(refresh_token: str) -> dict
│    def logout(refresh_token: str) -> None

modules/backend/services/connection.py (86 lines):
│class ConnectionService:
│    def __init__(session: AsyncSession) -> None
│    def create(user_id: UUID, exchange: str, product_types: list[str], label: str, api_key: str, api_secret: str) -> dict
│    def update(connection_id: UUID, user_id: UUID) -> object
│    def delete(connection_id: UUID, user_id: UUID) -> None
│    def get_by_user(user_id: UUID) -> list
│    def get_owned(connection_id: UUID, user_id: UUID) -> object
│    def _get_owned(connection_id: UUID, user_id: UUID)

modules/backend/repositories/magic_link.py (43 lines):
│class MagicLinkRepository:
│    def get_valid_by_hash(token_hash: str) -> MagicLink | None
│    def consume(id: UUID) -> None
│    def cleanup_expired() -> int

modules/backend/api/__init__.py (1 lines):

modules/backend/api/v1/__init__.py (31 lines):

modules/backend/core/exception_handlers.py (253 lines):
│def _get_request_id(request: Request) -> str | None
│def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse
│def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse
│def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse
│def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse
│def register_exception_handlers(app: FastAPI) -> None

modules/backend/core/middleware.py (146 lines):
│class RequestContextMiddleware(BaseHTTPMiddleware):
│    def dispatch(request: Request, call_next: RequestResponseEndpoint) -> Response
│    def _add_security_headers(response: Response) -> None

modules/backend/schemas/views.py (50 lines):
│class DashboardView(BaseModel):
│    stats: DashboardStats
│    recent_positions: list[PositionSummary]
│    connections: list[ConnectionSummary]
│    has_connections: bool
│    has_positions: bool
│class PositionListView(BaseModel):
│    positions: list[PositionSummary]
│    filter_options: dict
│class SettingsView(BaseModel):
│    user: dict
│    storage_used_bytes: int
│    storage_limit_bytes: int
│    storage_used_pct: float
│class DashboardStats(BaseModel):
│    total_positions: int
│    open_positions: int
│    win_count: int
│    loss_count: int
│    win_rate_pct: float
│    total_pnl: str
│    avg_pnl: str | None
│    avg_win: str | None
│    avg_loss: str | None
│    best_trade: str | None
│    worst_trade: str | None
│class ConnectionSummary(BaseModel):
│    id: str
│    exchange: str
│    label: str
│    is_active: bool
│    last_sync_at: str | None
│    last_sync_ago: str | None
│    position_count: int
│    fill_count: int

modules/backend/schemas/attachment.py (20 lines):
│class LinkCreate(BaseModel):
│    url: str
│    caption: str | None
│class AttachmentResponse(BaseModel):
│    id: str
│    position_id: str
│    attachment_type: str
│    file_name: str | None
│    file_size_bytes: int | None
│    mime_type: str | None
│    url: str | None
│    caption: str | None
│    created_at: str

modules/backend/services/grouper/engine.py (292 lines):
│class _OpenPosition:
│    def __init__(symbol: str, direction: str, net_qty: Decimal, entry_cost: Decimal, total_entry_qty: Decimal, total_commission: Decimal, max_size_qty: Decimal, opened_at, fills: list[AssignedFill]) -> None
│def group_fills(fills: list[RawFill]) -> list[GroupedPosition]
│def _group_symbol_fills(symbol: str, fills: list[RawFill]) -> list[GroupedPosition]
│def _signed_qty(fill: RawFill) -> Decimal
│def _same_sign(a: Decimal, b: Decimal) -> bool
│def _open_new(fill: RawFill, qty_signed: Decimal) -> _OpenPosition
│def _add_entry(pos: _OpenPosition, fill: RawFill, qty_signed: Decimal) -> None
│def _add_exit(pos: _OpenPosition, fill: RawFill, close_qty: Decimal, ...) -> None
│def _close_position(pos: _OpenPosition, closing_fill: RawFill) -> GroupedPosition

modules/backend/services/grouper/reconciler.py (100 lines):
│def reconcile(new_positions: list[GroupedPosition], existing: list[dict]) -> dict
│def _find_match(pos: GroupedPosition, existing: list[dict], already_matched: set[str]) -> dict | None

modules/backend/__init__.py (1 lines):

modules/backend/api/health.py (185 lines):
│@router.get
│def health_check() -> dict[str, str]
│@router.get
│def readiness_check() -> dict[str, Any]
│@router.get
│def detailed_health_check() -> dict[str, Any]
│def _get_pool_status() -> dict[str, Any]

modules/backend/api/v1/endpoints/attachments.py (131 lines):
│@router.post
│def upload_attachment(position_id: UUID, file: UploadFile, db: DbSession, ...) -> ApiResponse
│@router.post
│def add_link_attachment(position_id: UUID, body: LinkCreate, db: DbSession, ...) -> ApiResponse
│@router.delete
│def delete_attachment(attachment_id: UUID, db: DbSession, user: CurrentUser) -> None

modules/backend/api/v1/endpoints/auth.py (175 lines):
│@router.post
│def request_magic_link(body: MagicLinkRequest, db: DbSession) -> ApiResponse
│@router.post
│def verify_magic_link(body: VerifyRequest, db: DbSession, response: Response) -> ApiResponse[AuthResponse]
│@router.post
│def refresh_tokens(db: DbSession, refresh_token: RefreshToken, response: Response) -> ApiResponse[AuthResponse]
│@router.post
│def dev_login(body: MagicLinkRequest, db: DbSession, response: Response) -> ApiResponse[AuthResponse]
│@router.post
│def logout(db: DbSession, refresh_token: RefreshToken, response: Response) -> None

modules/backend/api/v1/endpoints/connections.py (98 lines):
│@router.post
│def create_connection(body: ConnectionCreate, db: DbSession, user: CurrentUser) -> ApiResponse[ConnectionResponse]
│@router.patch
│def update_connection(connection_id: UUID, body: ConnectionUpdate, db: DbSession, ...) -> ApiResponse
│@router.delete
│def delete_connection(connection_id: UUID, db: DbSession, user: CurrentUser) -> None
│@router.post
│def trigger_sync(connection_id: UUID, db: DbSession, user: CurrentUser) -> ApiResponse

modules/backend/api/v1/endpoints/events.py (75 lines):
│@router.get
│def stream_events(token: str)

modules/backend/api/v1/endpoints/export.py (87 lines):
│@router.get
│def export_positions(db: DbSession, user: CurrentUser, format: str, ...) -> StreamingResponse

modules/backend/api/v1/endpoints/notes.py (64 lines):
│@router.post
│def create_note(position_id: UUID, body: NoteCreate, db: DbSession, ...) -> ApiResponse
│@router.patch
│def update_note(note_id: UUID, body: NoteUpdate, db: DbSession, ...) -> ApiResponse
│@router.delete
│def delete_note(note_id: UUID, db: DbSession, user: CurrentUser) -> None

modules/backend/api/v1/endpoints/positions.py (38 lines):
│@router.patch
│def update_position(position_id: UUID, body: PositionUpdate, db: DbSession, ...) -> ApiResponse

modules/backend/api/v1/endpoints/users.py (47 lines):
│@router.patch
│def update_profile(body: UpdateUserRequest, user: CurrentUser, db: DbSession) -> ApiResponse[UserResponse]
│@router.delete
│def deactivate_account(user: CurrentUser, db: DbSession) -> None

modules/backend/api/v1/endpoints/views.py (239 lines):
│@router.get
│def dashboard_view(db: DbSession, user: CurrentUser) -> ApiResponse[DashboardView]
│@router.get
│def position_list_view(db: DbSession, user: CurrentUser, status: str | None, ...) -> ApiResponse[PositionListView]
│@router.get
│def position_detail_view(position_id: str, db: DbSession, user: CurrentUser) -> ApiResponse
│@router.get
│def connections_view(db: DbSession, user: CurrentUser) -> ApiResponse
│@router.get
│def settings_view(db: DbSession, user: CurrentUser) -> ApiResponse[SettingsView]
│def _mask_key(encrypted_bytes: bytes | None) -> str
│def _to_summary(p) -> PositionSummary

modules/backend/core/__init__.py (1 lines):

modules/backend/core/concurrency.py (167 lines):
│class TracedThreadPoolExecutor(ThreadPoolExecutor):
│    def submit()
│def get_io_pool() -> TracedThreadPoolExecutor
│def get_cpu_pool() -> ProcessPoolExecutor
│def get_interpreter_pool() -> Any
│def get_semaphore(name: str) -> asyncio.Semaphore
│def shutdown_pools() -> None

modules/backend/core/pagination.py (266 lines):
│class PaginationParams:
│    limit: int
│    offset: int
│    cursor: str | None
│    def is_cursor_based() -> bool
│class PagedResult:
│    items: list[T]
│    total: int | None
│    limit: int
│    offset: int
│    has_more: bool
│    next_cursor: str | None
│def get_pagination_params(limit: int | None, offset: int, cursor: str | None) -> PaginationParams
│def encode_cursor(value: str | int) -> str
│def decode_cursor(cursor: str) -> str
│def create_paginated_response(items: list[Any], item_schema: type[BaseModel], total: int | None, ...) -> dict[str, Any]
│def paginate_query(query_func, params: PaginationParams, count_func) -> PagedResult

modules/backend/core/resilience.py (136 lines):
│class ResilienceLogger(aiobreaker.CircuitBreakerListener):
│    def __init__(dependency: str) -> None
│    def state_change(cb: aiobreaker.CircuitBreaker, old_state: Any, new_state: Any) -> None
│    def failure(cb: aiobreaker.CircuitBreaker, exception: Exception) -> None
│def log_retry(retry_state: Any) -> None
│def create_circuit_breaker(dependency: str, fail_max: int, timeout_duration: int) -> aiobreaker.CircuitBreaker

modules/backend/events/__init__.py (1 lines):

modules/backend/events/broker.py (72 lines):
│def create_event_broker() -> RedisBroker
│def get_event_broker() -> RedisBroker
│def create_event_app() -> FastStream

modules/backend/events/consumers/__init__.py (1 lines):

modules/backend/events/middleware.py (65 lines):
│class EventObservabilityMiddleware(BaseMiddleware):
│    def on_consume(msg)
│    def after_consume(err)

modules/backend/events/publishers.py (44 lines):
│def _get_trace_id() -> str | None
│def publish_event(stream: str, event) -> None

modules/backend/events/schemas.py (52 lines):
│class EventEnvelope(BaseModel):
│    event_id: str
│    event_type: str
│    event_version: int
│    timestamp: str
│    source: str
│    correlation_id: str
│    trace_id: str | None
│    payload: dict
│class SyncStarted(EventEnvelope):
│    event_type: str
│class SyncProgress(EventEnvelope):
│    event_type: str
│class SyncCompleted(EventEnvelope):
│    event_type: str
│class SyncFailed(EventEnvelope):
│    event_type: str
│class IndicatorsReady(EventEnvelope):
│    event_type: str

modules/backend/main.py (147 lines):
│@asynccontextmanager
│def lifespan(app: FastAPI) -> AsyncGenerator[None, None]
│def _init_tracing(app: FastAPI, app_config) -> None
│def _init_metrics(app: FastAPI) -> None
│def create_app() -> FastAPI
│def get_app() -> FastAPI
│def __getattr__(name: str) -> FastAPI

modules/backend/migrations/env.py (115 lines):
│def get_database_url() -> str
│def run_migrations_offline() -> None
│def do_run_migrations(connection: Connection) -> None
│def run_async_migrations() -> None
│def run_migrations_online() -> None

modules/backend/migrations/versions/0392f98d1cc2_initial_journal_schema.py (269 lines):
│def upgrade() -> None
│def downgrade() -> None

modules/backend/models/__init__.py (25 lines):

modules/backend/repositories/__init__.py (4 lines):

modules/backend/repositories/candle.py (96 lines):
│class CandleRepository:
│    def __init__(session) -> None
│    def upsert_candles(candles: list[dict]) -> int
│    def get_for_snapshot(exchange: str, symbol: str, product_type: str, timeframe: str, since: datetime, limit: int) -> list[Candle]
│    def count_for_range(exchange: str, symbol: str, product_type: str, timeframe: str, since: datetime) -> int

modules/backend/schemas/__init__.py (16 lines):

modules/backend/services/__init__.py (1 lines):

modules/backend/services/base.py (204 lines):
│class BaseService:
│    def __init__(session: AsyncSession) -> None
│    def session() -> AsyncSession
│    def _execute_db_operation(operation: str, coro: Any) -> T
│    def _validate_required(fields: dict[str, Any], field_names: list[str]) -> None
│    def _validate_string_length(value: str, field_name: str, min_length: int | None, max_length: int | None) -> None
│    def _log_operation(operation: str) -> None
│    def _log_debug(message: str) -> None

modules/backend/services/email.py (58 lines):
│def send_magic_link_email(to_email: str, token: str, frontend_url: str) -> None
│def _has_resend(settings) -> bool
│def _send_via_resend(to_email: str, verify_url: str) -> None

modules/backend/services/exchange/__init__.py (1 lines):

modules/backend/services/exchange/binance_futures.py (242 lines):
│class BinanceFuturesAdapter:
│    def __init__() -> None
│    def _sign(params: dict, api_secret: str) -> str
│    def _headers(api_key: str) -> dict
│    def test_connection(api_key: str, api_secret: str) -> ConnectionTestResult
│    def fetch_fills_page(api_key: str, api_secret: str, symbol: str, product_type: str, cursor: dict | None) -> FillPage
│    def fetch_candles(symbol: str, product_type: str, timeframe: str, start_time: datetime, end_time: datetime | None, limit: int) -> list[CandleBar]
│    def fetch_open_interest(symbol: str, product_type: str, timeframe: str, start_time: datetime, limit: int) -> list[CandleBar]
│def _map_binance_fill(trade: dict, symbol: str, product_type: str) -> RawFill
│def _ts_now() -> int

modules/backend/services/exchange/bybit.py (340 lines):
│class BybitAdapter:
│    def __init__() -> None
│    def _auth_headers(api_key: str, api_secret: str, params: dict) -> dict
│    def test_connection(api_key: str, api_secret: str) -> ConnectionTestResult
│    def fetch_fills_page(api_key: str, api_secret: str, symbol: str, product_type: str, cursor: dict | None) -> FillPage
│    def fetch_candles(symbol: str, product_type: str, timeframe: str, start_time: datetime, end_time: datetime | None, limit: int) -> list[CandleBar]
│    def fetch_open_interest(symbol: str, product_type: str, timeframe: str, start_time: datetime, limit: int) -> list[CandleBar]
│def _map_bybit_fill(item: dict, product_type: str) -> RawFill
│def _product_to_category(product_type: str) -> str
│def _timeframe_to_interval(timeframe: str) -> str

modules/backend/services/exchange/rate_limiter.py (35 lines):
│def _rate_limit_key(exchange: str, api_key: str) -> str
│def enforce_exchange_rate_limit(redis, exchange: str, api_key: str, ...) -> None

modules/backend/services/grouper/__init__.py (1 lines):

modules/backend/services/indicators/__init__.py (1 lines):

modules/backend/services/indicators/engine.py (64 lines):
│def compute_snapshot(candles_by_timeframe: dict[str, pd.DataFrame], at_time: datetime | None) -> dict[str, dict[str, object]]

modules/backend/services/sync.py (302 lines):
│class SyncService:
│    def __init__(session: AsyncSession) -> None
│    def sync_connection(connection_id: UUID, user_id: UUID) -> dict
│    def _fetch_fills_for_product(adapter, api_key, api_secret, conn, product_type, all_symbols, uid) -> int
│def _fill_to_raw(fill)

modules/backend/tasks/__init__.py (26 lines):
│def __getattr__(name: str)

modules/backend/tasks/calculate_indicators.py (166 lines):
│@broker.task
│def calculate_indicators(position_id: str, user_id: str) -> dict
│def _compute_at_time(adapter, symbol: str, product_type: str, ...) -> dict[str, dict[str, object]]

modules/backend/tasks/cleanup.py (22 lines):
│@broker.task
│def cleanup_magic_links() -> dict

modules/backend/tasks/scheduler.py (79 lines):
│def create_scheduler() -> 'TaskiqScheduler'
│def get_scheduler() -> 'TaskiqScheduler'
│def __getattr__(name: str)

modules/backend/tasks/sync_trades.py (36 lines):
│@broker.task
│def sync_trades(connection_id: str, user_id: str) -> dict


## modules

modules/__init__.py (6 lines):


## frontend

modules/frontend/node_modules/flatted/python/flatted.py (144 lines):
│class _Known:
│    def __init__()
│class _String:
│    def __init__(value)
│def _array_keys(value)
│def _object_keys(value)
│def _is_array(value)
│def _is_object(value)
│def _is_string(value)
│def _index(known, input, value)
│def _relate(known, input, value)
│def _resolver(input, lazy, parsed)
│def _transform(known, input, value)
│def _wrap(value)
│def parse(value)
│def stringify(value)
