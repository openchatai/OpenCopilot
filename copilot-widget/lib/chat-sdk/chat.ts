import { AxiosInstance } from "axios";
import { Massenger } from ".";
import { HistoryMessage, SessionIdType, getInstance } from "./data";
import { radnom } from "./rand";
import get from 'lodash.get';

type ChatOptionsType = {
    copilotToken: string;
    baseUrl: string;
    inject?: {
        user?: Record<string, any>;
        headers?: Record<string, any>;
    }
}

export class Chat {
    private sessionId?: SessionIdType;
    history: HistoryMessage[] = [];
    options: ChatOptionsType;
    messenger: Massenger = new Massenger(this);
    axiosInstance: AxiosInstance | null = null;

    constructor(options: ChatOptionsType) {
        this.options = options;
        this.initAxios();
    }

    initAxios() {
        this.axiosInstance = getInstance({
            baseUrl: get(this.options, "baseUrl"),
            copilotToken: get(this.options, "copilotToken"),
            sessionId: this.getSessionId,
        });
    }

    get getSessionId(): SessionIdType {
        if (!this.sessionId) {
            this.setSessionId = this.generateSessionId();
        }
        return this.sessionId!;
    }

    set setSessionId(sessionId: SessionIdType) {
        this.sessionId = sessionId;
    }

    generateSessionId(): SessionIdType {
        return (radnom() + ":" + this.options.copilotToken) as SessionIdType;
    }

}