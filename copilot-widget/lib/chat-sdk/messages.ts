import get from "lodash.get";
import { radnom } from "./rand";

type Actor = "user" | "bot";
type IdType = string | number;
type TimeStampType = number | Date;

type UserMessageOptions = {
    timestamp?: TimeStampType;
    id?: IdType;
    from?: Actor;
    content: string;
}

export type UserMessagePayload = {
    message: string;
    id?: IdType;
    timestamp?: TimeStampType;
}
export class UserMessage {
    id: IdType;
    timestamp?: TimeStampType;
    from: Actor = "user";
    content: string;

    constructor(
        content: string,
        options?: UserMessageOptions
    ) {
        this.content = content;
        this.id = get(options, "id", radnom());
        this.timestamp = get(options, "timestamp", Date.now());
    }

    public get payload(): {
        content: string;
        id?: IdType;
        timestamp?: TimeStampType;
    } {
        return {
            content: this.content,
            id: this.id,
            timestamp: this.timestamp,
        }
    }
}

type CopilotMessageTypes = "text";

class CopilotResponse {
    id: IdType;
    timestamp: TimeStampType;
    from: Actor = "bot";
    type: CopilotMessageTypes;
    private userMessageId: IdType | null = null;

    constructor({
        type,
        id,
        timestamp = Date.now(),
    }: { type: CopilotMessageTypes, id: IdType, timestamp?: TimeStampType }) {
        this.type = type;
        this.id = id;
        this.timestamp = timestamp;

    }
    public set setUserMessageId(id: IdType) {
        this.userMessageId = id;
    }
    public get getUserMessageId() {
        return this.userMessageId;
    }
}
export class CopilotTextResponse extends CopilotResponse {
    response: string;

    constructor(response: string, id?: IdType) {
        super({ type: "text", id: id || radnom() });
        this.response = response;
    }

    public get payload(): {
        response: string;
        id?: IdType;
        timestamp?: TimeStampType;
    } {
        return {
            response: this.response,
            id: this.id,
            timestamp: this.timestamp,
        }
    }
}


export type MessageType = CopilotTextResponse | UserMessage;