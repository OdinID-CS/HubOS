import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme, type ThemePreference } from "../../app/providers";

const themeOptions: Array<{
  value: ThemePreference;
  label: string;
  Icon: typeof Sun;
}> = [
  { value: "system", label: "Use system theme", Icon: Monitor },
  { value: "light", label: "Use light theme", Icon: Sun },
  { value: "dark", label: "Use dark theme", Icon: Moon },
];

export function ThemeToggle() {
  const { preference, setPreference } = useTheme();

  return (
    <div className="theme-switch" role="group" aria-label="Color theme">
      {themeOptions.map(({ value, label, Icon }) => (
        <button
          key={value}
          type="button"
          className="theme-switch__button"
          aria-label={label}
          aria-pressed={preference === value}
          title={label}
          onClick={() => setPreference(value)}
        >
          <Icon size={15} aria-hidden="true" />
        </button>
      ))}
    </div>
  );
}
