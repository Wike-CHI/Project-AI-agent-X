## ADDED Requirements

### Requirement: Short-Term Memory Management
系统 SHALL 管理会话内的短期记忆，支持存储和检索。

#### Scenario: Store short-term memory
- **WHEN** user requests to store a short-term memory
- **THEN** the system SHALL create a memory record with type "short_term" and expiration time

#### Scenario: Retrieve short-term memories
- **WHEN** user requests short-term memories
- **THEN** the system SHALL return all non-expired short-term memories for the current session

#### Scenario: Automatic short-term memory conversion
- **WHEN** a conversation session ends
- **THEN** the system SHALL convert important short-term memories to long-term memory

### Requirement: Long-Term Memory Management
系统 SHALL 持久化长期记忆，支持语义检索和自动管理。

#### Scenario: Store long-term memory
- **WHEN** user requests to store a long-term memory
- **THEN** the system SHALL create a memory record with embedding and persist to vector store

#### Scenario: Retrieve long-term memories by semantic search
- **WHEN** user searches long-term memories with a query
- **THEN** the system SHALL perform semantic search and return matching memories sorted by relevance

#### Scenario: Automatic memory summarization
- **WHEN** long-term memories exceed storage threshold
- **THEN** the system SHALL create a summary memory and mark original for potential cleanup

### Requirement: Memory Importance Scoring
系统 SHALL 自动评估和更新记忆的重要性评分。

#### Scenario: Initial importance scoring
- **WHEN** a memory is created
- **THEN** the system SHALL assign an initial importance score based on content analysis

#### Scenario: Update importance on access
- **WHEN** a memory is accessed or referenced
- **THEN** the system SHALL increment its importance score

### Requirement: Memory Expiration and Cleanup
系统 SHALL 自动清理过期和低重要性的记忆。

#### Scenario: Expire short-term memories
- **WHEN** a short-term memory exceeds its expiration time
- **THEN** the system SHALL mark it as expired and exclude from retrieval

#### Scenario: Cleanup low-importance long-term memories
- **WHEN** long-term memory importance drops below threshold
- **THEN** the system SHALL archive the memory after retention period

### Requirement: Memory Relationship Tracking
系统 SHALL 跟踪记忆之间的关系和关联。

#### Scenario: Link related memories
- **WHEN** user explicitly links two memories
- **THEN** the system SHALL create a relationship record between them

#### Scenario: Discover related memories
- **WHEN** user requests related memories for a given memory
- **THEN** the system SHALL return memories connected via explicit or semantic relationships
