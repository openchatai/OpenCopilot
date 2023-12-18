import { Chat } from "./chat";
import { CopilotTextResponse, MessageType, UserMessage } from "./messages";

export class Massenger {
    // responsible for sending,storing messages
    private messages: Set<MessageType> = new Set();

    chat: Chat;

    constructor(chat: Chat) {
        this.chat = chat;
    }

    private get axios() {
        return this.chat.axiosInstance
    }

    private set addMessage(message: MessageType) {
        this.messages.add(message)
    }

    public get getMessages() {
        return this.messages;
    }

    public clearMessages() {
        this.messages.clear();
    }

    public queryMessage(id: string | number) {
        // query message by id
        return [...this.messages].find((message) => message.id === id);
    }

    async handleMessage(message: UserMessage) {
        if (!this.axios) {
            throw new Error("axios is not initialized");
        }
        // Currently we only support text messages
        const { data, status } = await this.axios.post<{
            type: "text",
            response: {
                text: string | null
            }
        }>("/chat/send", message.payload);

        if (status !== 200) {
            throw new Error("Failed to send message");
        }
        
        if (data.type === 'text') {
            const copilotResp = new CopilotTextResponse(data.response.text || 'null')
            copilotResp.setUserMessageId = message.id;
            this.addMessage = copilotResp;
        }
    }

    async sendMessage(message: string) {
        const userMessage = new UserMessage(message);
        this.addMessage = userMessage;
        await this.handleMessage(userMessage);
    }
    toArray() {
        return [...this.messages]
    }

}
