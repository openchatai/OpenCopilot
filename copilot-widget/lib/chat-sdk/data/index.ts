import axios, { AxiosInstance } from "axios";

export type SessionIdType = `${string}:${string}`;
const SESSION_ID_HEADER = "X-Session-Id";
const COPILOT_TOKEN_HEADER = "X-Bot-Token";

type InstanceOptions = {
    copilotToken: string;
    sessionId: SessionIdType;
    baseUrl: string;
}

// only one instance per copilotToken
let instances = new Map<string, AxiosInstance>();

export function getInstance(
    {
        copilotToken,
        sessionId,
        baseUrl,
    }: InstanceOptions,
) {
    // make sure we only have one instance
    if (!instances.has(copilotToken)) {
        const instance = axios.create({
            baseURL: baseUrl,
            headers: {
                [SESSION_ID_HEADER]: sessionId,
                [COPILOT_TOKEN_HEADER]: copilotToken,
            },
        });
        instances.set(copilotToken, instance);
    }
    return instances.get(copilotToken)!;
}

export function getInitialData(instance: AxiosInstance) {
    return instance.get<InitialDataType>("/chat/init");
}

export type HistoryMessage = {
    chatbot_id: string;
    created_at: string;
    from_user: boolean;
    id: number;
    message: string;
    session_id: string;
    updated_at: string;
};

export interface InitialDataType {
    bot_name: string;
    logo: string;
    history: HistoryMessage[];
    sound_effects: {
        submit: string;
        response: string;
    };
    inital_questions: string[];
}
