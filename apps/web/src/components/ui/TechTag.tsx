export function TechTag({ tag, primary }: { tag: string; primary: boolean }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border ${
      primary
        ? 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30'
        : 'bg-neutral-100 text-neutral-600 border-neutral-200'
    }`}>
      {tag}
    </span>
  );
}
