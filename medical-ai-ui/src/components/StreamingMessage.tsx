interface StreamingMessageProps {
  content: string;
}

export const StreamingMessage = ({ content }: StreamingMessageProps) => {
  return (
    <div className="flex justify-start">
      <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-200 text-gray-900">
        <p className="whitespace-pre-wrap">{content}</p>
        <span className="inline-block w-2 h-4 bg-gray-500 animate-pulse ml-1"></span>
      </div>
    </div>
  );
};