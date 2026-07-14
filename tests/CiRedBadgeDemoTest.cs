using NUnit.Framework;

namespace CatacombsOfYarl.Tests;

/// <summary>
/// THROWAWAY — DO NOT MERGE.
///
/// This single always-failing test exists only to demonstrate that a red CI status is
/// visible on a PR (M0 exit-gate clause 2). It is isolated: it weakens no real test and
/// touches no product code. The branch chore/ci-red-badge-demo is opened as a PR purely so
/// the failing "Balance Suite" check can be eyeballed, then closed WITHOUT merging.
/// </summary>
[TestFixture]
public class CiRedBadgeDemoTest
{
    [Test]
    public void DeliberatelyFails_ToProveRedCiIsVisible()
    {
        Assert.Fail("Intentional failure — CI red-badge visibility demo (M0 item 2). Do not merge; close this PR.");
    }
}
