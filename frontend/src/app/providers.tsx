import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createContext,
  useContext,
  useEffect,
  useLayoutEffect,
  useState,
  type ReactNode,
} from "react";

type AppProvidersProps = {
  children: ReactNode;
};

export type ThemePreference = "system" | "light" | "dark";

type ThemeContextValue = {
  preference: ThemePreference;
  setPreference: (preference: ThemePreference) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

function isThemePreference(value: string | null): value is ThemePreference {
  return value === "system" || value === "light" || value === "dark";
}

function readThemePreference(): ThemePreference {
  try {
    const storedPreference = window.localStorage.getItem("hubos-theme");
    return isThemePreference(storedPreference) ? storedPreference : "system";
  } catch (error) {
    console.error("Unable to read the saved theme preference.", error);
    return "system";
  }
}

function applyTheme(preference: ThemePreference) {
  const isDark =
    preference === "dark" ||
    (preference === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);
  const theme = isDark ? "dark" : "light";

  document.documentElement.dataset.theme = theme;
  const background = getComputedStyle(document.documentElement)
    .getPropertyValue("--background")
    .trim();
  document
    .querySelector<HTMLMetaElement>('meta[name="theme-color"]')
    ?.setAttribute("content", background);
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within AppProviders.");
  }
  return context;
}

export function AppProviders({ children }: AppProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );
  const [preference, setPreference] = useState(readThemePreference);

  useLayoutEffect(() => {
    applyTheme(preference);
    try {
      window.localStorage.setItem("hubos-theme", preference);
    } catch (error) {
      console.error("Unable to save the theme preference.", error);
    }
  }, [preference]);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleSystemThemeChange = () => {
      if (preference === "system") {
        applyTheme("system");
      }
    };

    mediaQuery.addEventListener("change", handleSystemThemeChange);
    return () =>
      mediaQuery.removeEventListener("change", handleSystemThemeChange);
  }, [preference]);

  return (
    <ThemeContext.Provider value={{ preference, setPreference }}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </ThemeContext.Provider>
  );
}
